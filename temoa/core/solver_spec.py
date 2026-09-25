"""
Solver selection and option resolution.

The config accepts ``solver`` as either a plain solver name or a table with a ``name`` and a
passthrough ``options`` table.  Options that reach the solver are layered as:

    DEFAULT_SOLVER_OPTIONS  <  [solver.options]  <  extension-specific options (MGA, MC, ...)

Any solver name known to pyomo's SolverFactory is accepted.  Solvers without an entry in
DEFAULT_SOLVER_OPTIONS simply get no Temoa defaults.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

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


def resolve_solver_options(
    spec: SolverSpec,
    extension_options: Mapping[str, Any] | None = None,
    *,
    include_defaults: bool = True,
) -> dict[str, Any]:
    """
    Merge the option layers that are passed to the solver
    :param spec: the solver spec from the config
    :param extension_options: options from an extension's own source (MGA/MC/Morris toml,
    stochastic config), which take precedence over everything else
    :param include_defaults: include DEFAULT_SOLVER_OPTIONS as the bottom layer.  Solve paths that
    historically ran without Temoa defaults (MGA base solve, stochastic) turn this off.
    :return: a new dict of solver options
    """
    defaults = DEFAULT_SOLVER_OPTIONS.get(spec.name, {}) if include_defaults else {}
    return {**defaults, **spec.options, **(extension_options or {})}
