"""
Lightweight LP comparison helper, extracted from compare_lp.py.

Parses two LP files and returns a structured diff, without writing reports
to disk.  Intended for use by the reserve margin regression test.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

_CAMEL_RE = re.compile(r'([a-z0-9])([A-Z])')
_TERM_RE = re.compile(r'^([+\-]?\s*\d*\.?\d+(?:[eE][+\-]?\d+)?)\s+(\S+)$')
_RELATION_RE = re.compile(r'^([<>=]=?)\s*([\d.eE+\-]+)$')


def _camel_to_snake(s: str) -> str:
    return _CAMEL_RE.sub(r'\1_\2', s).lower()


def _norm(token: str) -> str:
    paren = token.find('(')
    if paren == -1:
        return _camel_to_snake(token)
    return _camel_to_snake(token[:paren]) + token[paren:]


def _needs_normalization(path: Path, sample: int = 2000) -> bool:
    checked = 0
    with path.open(encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            s = raw.strip()
            if not s or s.startswith('\\') or s.startswith('*'):
                continue
            line = re.sub(r'^([+\-])\s+', r'\1', s)
            m = _TERM_RE.match(line)
            token = None
            if m:
                token = m.group(2)
            elif s.endswith(':') and not s.startswith(('+', '-')):
                token = s.rstrip(':').rstrip('_')
            if token:
                paren = token.find('(')
                name = token[:paren] if paren != -1 else token
                if _CAMEL_RE.search(name):
                    return True
            checked += 1
            if checked >= sample:
                break
    return False


def _stream(path: Path, normalize: bool) -> Generator[tuple[Any, ...]]:
    tok = _norm if normalize else (lambda t: t)
    section = 'preamble'
    obj_name = None
    obj_terms: list[tuple[float, str]] = []
    con_label: str | None = None
    con_terms: list[tuple[float, str]] = []
    con_rel: str | None = None
    con_rhs: float | None = None

    def _flush() -> tuple[str, str, list[tuple[float, str]], str | None, float | None] | None:
        nonlocal con_label, con_terms, con_rel, con_rhs
        result: tuple[str, str, list[tuple[float, str]], str | None, float | None] | None = None
        if con_label is not None and con_rel is not None:
            result = ('con', con_label, list(con_terms), con_rel, con_rhs)
        con_label = None
        con_terms = []
        con_rel = None
        con_rhs = None
        return result

    with path.open(encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            s = raw.strip()
            if not s:
                continue
            lower = s.lower()

            if lower in ('s.t.', 'subject to', 'st'):
                if section == 'objective' and obj_terms:
                    yield ('obj', obj_name, obj_terms)
                section = 'constraints'
                continue

            if lower in ('bounds', 'generals', 'general', 'binary', 'binaries', 'end'):
                r = _flush()
                if r:
                    yield r
                if section == 'objective' and obj_terms:
                    yield ('obj', obj_name, obj_terms)
                yield ('bounds_start',)
                section = 'done'
                continue

            if section == 'done' or s.startswith('\\') or s.startswith('*'):
                continue

            if section == 'preamble':
                if lower in ('min', 'max'):
                    section = 'objective'
                continue

            if section == 'objective':
                if s.endswith(':') and not s.startswith(('+', '-')):
                    obj_name = tok(s.rstrip(':'))
                    continue
                line = re.sub(r'^([+\-])\s+', r'\1', s)
                m = _TERM_RE.match(line)
                if m:
                    obj_terms.append((float(m.group(1).replace(' ', '')), tok(m.group(2))))
                continue

            if section == 'constraints':
                if s.endswith(':') and not s.startswith(('+', '-')):
                    r = _flush()
                    if r:
                        yield r
                    con_label = tok(s.rstrip(':').rstrip('_'))
                    continue
                m = _RELATION_RE.match(s)
                if m:
                    con_rel, con_rhs = m.group(1), float(m.group(2))
                    continue
                line = re.sub(r'^([+\-])\s+', r'\1', s)
                m = _TERM_RE.match(line)
                if m:
                    con_terms.append((float(m.group(1).replace(' ', '')), tok(m.group(2))))

    r = _flush()
    if r:
        yield r
    if section == 'objective' and obj_terms:
        yield ('obj', obj_name, obj_terms)


def _to_dict(terms: list[tuple[float, str]]) -> dict[str, float]:
    d: dict[str, float] = defaultdict(float)
    for c, v in terms:
        d[v] += c
    return dict(d)


@dataclass
class ConstraintDiff:
    label: str
    relation_changed: tuple[str, str] | None = None  # (rel1, rel2)
    rhs_changed: tuple[float, float] | None = None  # (rhs1, rhs2)
    terms_added: dict[str, float] = field(default_factory=dict)
    terms_removed: dict[str, float] = field(default_factory=dict)
    terms_changed: dict[str, tuple[float, float]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(
            self.relation_changed
            or self.rhs_changed
            or self.terms_added
            or self.terms_removed
            or self.terms_changed
        )


@dataclass
class LpDiff:
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)
    changed: list[ConstraintDiff] = field(default_factory=list)
    obj_diff: list[str] = field(default_factory=list)  # human-readable lines

    @property
    def is_identical(self) -> bool:
        return not (self.only_in_a or self.only_in_b or self.changed or self.obj_diff)

    def summary(self) -> str:
        lines = [
            f'only in A : {len(self.only_in_a)}',
            f'only in B : {len(self.only_in_b)}',
            f'changed   : {len(self.changed)}',
            f'obj diffs : {len(self.obj_diff)}',
        ]
        if self.only_in_a:
            lines.append('  A-only (first 10): ' + ', '.join(self.only_in_a[:10]))
        if self.only_in_b:
            lines.append('  B-only (first 10): ' + ', '.join(self.only_in_b[:10]))
        for cd in self.changed[:5]:
            lines.append(f'  changed: {cd.label}')
            if cd.relation_changed:
                lines.append(f'    relation: {cd.relation_changed[0]} → {cd.relation_changed[1]}')
            if cd.rhs_changed:
                lines.append(f'    rhs: {cd.rhs_changed[0]:+g} → {cd.rhs_changed[1]:+g}')
            for v, (c1, c2) in list(cd.terms_changed.items())[:3]:
                lines.append(f'    coeff {v}: {c1:+g} → {c2:+g}')
        return '\n'.join(lines)


def compare_lp_files(path_a: Path, path_b: Path, rtol: float = 1e-6) -> LpDiff:
    """
    Compare two LP files and return a structured diff.

    Auto-detects CamelCase vs snake_case naming and normalises both sides
    when either file uses CamelCase, so mixed-format comparisons work correctly.
    """
    apply_norm = _needs_normalization(path_a) or _needs_normalization(path_b)

    # Load file A into memory
    cons_a: dict[str, tuple[dict[str, float], str, float]] = {}
    obj_a: tuple[str | None, dict[str, float]] | None = None
    for block in _stream(path_a, apply_norm):
        if block[0] == 'obj':
            obj_a = (block[1], _to_dict(block[2]))
        elif block[0] == 'con':
            _, label, terms, rel, rhs = block
            cons_a[label] = (_to_dict(terms), rel, rhs)
        elif block[0] == 'bounds_start':
            break

    diff = LpDiff()
    seen: set[str] = set()
    obj_b: tuple[str | None, dict[str, float]] | None = None

    for block in _stream(path_b, apply_norm):
        if block[0] == 'obj':
            obj_b = (block[1], _to_dict(block[2]))
        elif block[0] == 'con':
            _, label, terms, rel, rhs = block
            td = _to_dict(terms)
            if label not in cons_a:
                diff.only_in_b.append(label)
            else:
                seen.add(label)
                td_a, rel_a, rhs_a = cons_a[label]
                cd = ConstraintDiff(label=label)
                if rel_a != rel:
                    cd.relation_changed = (rel_a, rel)
                if abs(rhs_a - rhs) > rtol * max(abs(rhs_a), abs(rhs), 1e-15):
                    cd.rhs_changed = (rhs_a, rhs)
                all_vars = sorted(set(td_a) | set(td))
                for v in all_vars:
                    c1, c2 = td_a.get(v), td.get(v)
                    if c1 is None:
                        cd.terms_added[v] = c2  # type: ignore[assignment]
                    elif c2 is None:
                        cd.terms_removed[v] = c1
                    else:
                        tol = rtol * max(abs(c1), abs(c2), 1e-15)
                        if abs(c1 - c2) > tol:
                            cd.terms_changed[v] = (c1, c2)
                if cd:
                    diff.changed.append(cd)
        elif block[0] == 'bounds_start':
            break

    diff.only_in_a = [lbl for lbl in cons_a if lbl not in seen]

    if obj_a and obj_b:
        all_vars = sorted(set(obj_a[1]) | set(obj_b[1]))
        for v in all_vars:
            c1, c2 = obj_a[1].get(v), obj_b[1].get(v)
            if c1 is None:
                diff.obj_diff.append(f'ADDED   {v} coeff={c2:+g}')
            elif c2 is None:
                diff.obj_diff.append(f'REMOVED {v} coeff={c1:+g}')
            else:
                tol = rtol * max(abs(c1), abs(c2), 1e-15)
                if abs(c1 - c2) > tol:
                    diff.obj_diff.append(f'CHANGED {v} {c1:+g} → {c2:+g}')

    return diff
