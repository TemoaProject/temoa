from __future__ import annotations

from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)


class TechCapacityVectorManager(TechActivityVectorManager):
    def map_variables(self) -> None:
        capacity = self.base_model.v_capacity_available_by_period_and_tech
        for idx in capacity:
            tech = idx[2]
            self.technology_size[tech] += 1
            self.variable_index_mapping[tech][capacity.name].append(idx)
