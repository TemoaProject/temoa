"""
Solver selection and option resolution.

The config accepts ``solver`` as either a plain solver name or a table with a ``name`` and a
passthrough ``options`` table.  Options that reach the solver are layered as:

    DEFAULT_SOLVER_OPTIONS  <  extension options file  <  [solver.options]  <  mode options

The extension options files (e.g. MGA_solver_options.toml) only hold fallback values, so the
config always wins over them.  Mode options are the solver_options of a mode section of the config
(e.g. [MGA]), which apply to the solves of that mode only.

Any solver name known to pyomo's SolverFactory is accepted.  Solvers without an entry in
DEFAULT_SOLVER_OPTIONS simply get no Temoa defaults.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from logging import getLogger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable
    from pathlib import Path

logger = getLogger(__name__)

# Note: these parameter values match mip-dev / PyPSA
# (see: https://pypsa-eur.readthedocs.io/en/latest/configuration.html)
DEFAULT_SOLVER_OPTIONS: dict[str, dict[str, Any]] = {
    'cplex': {
        'lpmethod': 4,  # barrier
        'solutiontype': 2,  # non basic solution, ie no crossover
        'barrier convergetol': 1.0e-3,
        'feasopt tolerance': 1.0e-4,
    },
    'gurobi': {
        'Method': 2,  # barrier
        'Crossover': 0,  # non basic solution, ie no crossover
        'BarConvTol': 1.0e-3,
        'FeasibilityTol': 1.0e-4,
        'BarOrder': -1,  # auto ordering; 2-4x faster than AMD on large models
    },
}


@dataclass(frozen=True, slots=True)
class SolverSpec:
    """A solver name plus the user-supplied options from the config (defaults excluded)."""

    name: str
    options: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def parse(cls, raw: str | Mapping[str, Any] | SolverSpec) -> SolverSpec:
        """
        Build a SolverSpec from a solver name, a {'name': ..., 'options': {...}} mapping, or an
        existing SolverSpec
        """
        if isinstance(raw, SolverSpec):
            return raw
        if isinstance(raw, str):
            if not raw:
                raise ValueError('Solver name must not be empty')
            return cls(raw)
        if isinstance(raw, Mapping):
            unknown = set(raw) - {'name', 'options'}
            if unknown:
                raise ValueError(
                    f'Unrecognized key(s) in solver table: {sorted(unknown)}.  Expected "name" '
                    'and (optionally) "options".  Solver parameters belong under [solver.options]'
                )
            name = raw.get('name')
            if not isinstance(name, str) or not name:
                raise ValueError('The solver table requires a non-empty "name" entry')
            options = raw.get('options', {})
            if not isinstance(options, Mapping):
                raise ValueError('The "options" entry of the solver table must be a table/dict')
            return cls(name, dict(options))
        raise TypeError(f'solver must be a str or a table/dict, got: {type(raw).__name__}')


# substrings (lowercase) of option names whose values are credentials, e.g. gurobi's WLSSecret,
# CloudSecretKey, CSAPIAccessID, ServerPassword, LicenseID
_SENSITIVE_OPTION_MARKERS = ('secret', 'password', 'accessid', 'licenseid', 'key', 'token')


def redact_solver_options(options: Mapping[str, Any]) -> dict[str, Any]:
    """
    Return a copy of the options that is safe to log or print, with credential values masked
    """
    return {
        option: '***'
        if any(marker in option.lower() for marker in _SENSITIVE_OPTION_MARKERS)
        else option_value
        for option, option_value in options.items()
    }


def resolve_solver_options(
    spec: SolverSpec,
    extension_options: Mapping[str, Any] | None = None,
    *,
    include_defaults: bool = True,
    fallback_options: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Merge the option layers that are passed to the solver
    :param spec: the solver spec from the config
    :param extension_options: options specific to the run mode (solver_options of a mode section
    of the config, stochastic config), which take precedence over everything else
    :param include_defaults: include DEFAULT_SOLVER_OPTIONS as the bottom layer.  Solve paths that
    historically ran without Temoa defaults (MGA base solve, stochastic) turn this off.
    :param fallback_options: options from an extension options file (MGA/MOO/MC/Morris toml),
    which only apply when the config does not set them
    :return: a new dict of solver options
    """
    defaults = DEFAULT_SOLVER_OPTIONS.get(spec.name, {}) if include_defaults else {}
    return {
        **defaults,
        **(fallback_options or {}),
        **spec.options,
        **(extension_options or {}),
    }


def read_options_file(source: Traversable | Path) -> dict[str, Any]:
    """Read an extension options file, e.g. MGA_solver_options.toml.

    Args:
        source: The options file.

    Returns:
        The content of the file, empty if the file is missing.
    """
    try:
        with source.open('rb') as f:
            return tomllib.load(f)
    except FileNotFoundError:
        logger.warning(
            'Unable to find the solver options file %s.  Using no options from it.', source
        )
        return {}


def mode_solver_options(mode_inputs: Mapping[str, Any] | None, mode: str) -> dict[str, Any]:
    """The solver_options of a mode section of the config"""
    raw = (mode_inputs or {}).get('solver_options')
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ValueError(
            f'solver_options in the [{mode}] section must be a table of solver options'
        )
    return dict(raw)


def resolve_num_workers(
    mode_inputs: Mapping[str, Any] | None, file_options: Mapping[str, Any], mode: str
) -> int:
    """The num_workers of a mode section of the config, else of the extension file, else 1"""
    raw = (mode_inputs or {}).get('num_workers', file_options.get('num_workers', 1))
    try:
        num_workers = int(raw)
    except (TypeError, ValueError) as err:
        raise ValueError(f'num_workers of {mode} must be an integer, got: {raw!r}') from err
    if num_workers < 1:
        raise ValueError(f'num_workers of {mode} must be at least 1, got: {num_workers}')
    return num_workers
