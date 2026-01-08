import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Perturbation:
    scenario: str
    table: str
    filter: dict[str, Any]
    action: str  # 'multiply', 'add', 'set'
    value: float

    def __post_init__(self) -> None:
        allowed_actions = {'multiply', 'add', 'set'}
        if self.action not in allowed_actions:
            raise ValueError(
                f"Invalid perturbation action '{self.action}'; must be one of {allowed_actions}"
            )


@dataclass
class StochasticConfig:
    scenarios: dict[str, float]  # scenario_name -> probability
    perturbations: list[Perturbation] = field(default_factory=list)
    solver_options: dict[str, Any] = field(default_factory=dict)


    @classmethod
    def from_toml(cls, path: Path) -> 'StochasticConfig':
        with open(path, 'rb') as f:
            data = tomllib.load(f)

        scenarios_raw = data.get('scenarios', {})
        scenarios = {}
        for name, val in scenarios_raw.items():
            if isinstance(val, dict):
                scenarios[name] = float(val.get('probability', 1.0))
            else:
                scenarios[name] = float(val)

        # Validate probability distribution
        if scenarios:
            total_prob = sum(scenarios.values())
            if not (0.99 <= total_prob <= 1.01):
                logger.warning(
                    'Stochastic scenario probabilities sum to %s; usually they should sum to ~1.0',
                    total_prob,
                )

        perturbations_data = data.get('perturbations', [])
        perturbations = []
        for i, p in enumerate(perturbations_data):
            try:
                scenario_name = p['scenario']
                if scenario_name not in scenarios:
                    raise ValueError(
                        f'Perturbation at index {i} references nonexistent scenario: '
                        f"'{scenario_name}'. Available scenarios: {list(scenarios.keys())}"
                    )

                perturbations.append(
                    Perturbation(
                        scenario=scenario_name,
                        table=p['table'],
                        filter=p['filter'],
                        action=p.get('action', 'set'),
                        value=p['value'],
                    )
                )
            except KeyError as e:
                raise ValueError(f'Perturbation at index {i} is missing required field: {e}') from e

        solver_options = data.get('solver_options', {})

        # Validate at least one scenario exists
        if not scenarios:
            raise ValueError('Stochastic configuration must define at least one scenario')

        return cls(
            scenarios=scenarios,
            perturbations=perturbations,
            solver_options=solver_options,
        )
