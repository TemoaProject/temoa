from __future__ import annotations

from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.core import value

from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


class TechEmissionVectorManager(TechActivityVectorManager):
    emission_commodities: list[str]
    emission_rates: defaultdict[str, defaultdict[str, list[float]]]

    def map_variables(self) -> None:
        model = self.base_model
        self.emission_commodities = self.selected_emission_commodities()
        self.emission_rates = defaultdict(lambda: defaultdict(list))

        rates: defaultdict[tuple[Any, ...], float] = defaultdict(float)
        for r, e, i, t, v, o in model.emission_activity.sparse_keys():
            if e in self.emission_commodities:
                rates[r, i, t, v, o] += value(model.emission_activity[r, e, i, t, v, o])

        for idx in model.active_flow_rpsditvo or set():
            r, _p, _s, _d, i, t, v, o = idx
            rate = rates.get((r, i, t, v, o))
            if rate:
                self.add_variable(t, model.v_flow_out.name, idx, rate)
        for idx_annual in model.active_flow_rpitvo or set():
            r, _p, i, t, v, o = idx_annual
            rate = rates.get((r, i, t, v, o))
            if rate and t in model.tech_annual:
                self.add_variable(t, model.v_flow_out_annual.name, idx_annual, rate)

    def add_variable(self, tech: str, var_name: str, idx: tuple[Any, ...], rate: float) -> None:
        self.technology_size[tech] += 1
        self.variable_index_mapping[tech][var_name].append(idx)
        self.emission_rates[tech][var_name].append(rate)

    def tech_terms(self, tech: str) -> list[tuple[str, Any, float]]:
        return [
            (var_name, idx, rate)
            for var_name, indices in self.variable_index_mapping[tech].items()
            for idx, rate in zip(indices, self.emission_rates[tech][var_name], strict=True)
        ]

    def tech_variables(self, model: TemoaModel, tech: str) -> list[Any]:
        rates = [
            rate
            for var_name in self.variable_index_mapping[tech]
            for rate in self.emission_rates[tech][var_name]
        ]
        variables = super().tech_variables(model, tech)
        return [rate * var for rate, var in zip(rates, variables, strict=True)]

    def selected_emission_commodities(self) -> list[str]:
        mga_inputs = getattr(self.config, 'mga_inputs', None) or {}
        selected = mga_inputs.get('axis_emission_commodities')
        if isinstance(selected, str):
            selected = [selected]
        if not isinstance(selected, (list, tuple)) or len(selected) == 0:
            raise ValueError(
                'MGA axis TECH_CATEGORY_EMISSION requires the "axis_emission_commodities" '
                'option in the [MGA] section of the config file, ex:  '
                'axis_emission_commodities = ["co2"]'
            )
        available = set(self.base_model.commodity_emissions)
        unknown = [e for e in selected if e not in available]
        if unknown:
            raise ValueError(
                f'MGA axis_emission_commodities {unknown} are not emission commodities in the '
                f'model.  Available: {sorted(available)}'
            )
        logger.info('MGA emission axis uses the emissions of: %s', list(selected))
        return [str(e) for e in selected]
