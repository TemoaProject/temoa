# temoa/components/emissions.py
"""
Defines the components of the Temoa model related to emissions accounting.

This module is responsible for:
-  Defining index sets for emission-related parameters and constraints.
-  Defining the constraint rule for 'linked technologies', a special case where
    an emission commodity (e.g., captured CO2) is also treated as a physical
    input to a downstream process (e.g., synthetic fuel production).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyomo.core import quicksum
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import ExprLike
    from temoa.types.core_types import (
        Commodity,
        Period,
        Region,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def emission_activity_indices(
    model: TemoaModel,
) -> set[tuple[Region, Commodity, Commodity, Technology, Vintage, Commodity]]:
    indices = {
        (r, e, i, t, v, o)
        for r, i, t, v, o in model.efficiency.sparse_iterkeys()
        for e in model.commodity_emissions
        if r in model.regions  # omit any exchange/groups
    }

    return indices


def linked_tech_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage, Commodity]]:
    linkedtech_indices = {
        (r, p, s, d, t, v, e)
        for r, t, e in model.linked_techs.sparse_iterkeys()
        for p in model.time_optimize
        if (r, p, t) in model.process_vintages
        for v in model.process_vintages[r, p, t]
        if model.active_activity_rptv and (r, p, t, v) in model.active_activity_rptv
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    return linkedtech_indices


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def linked_emissions_tech_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
    e: Commodity,
) -> ExprLike:
    r"""
    This constraint is necessary for carbon capture technologies that produce
    CO2 as an emissions commodity, but the CO2 also serves as a physical
    input commodity to a downstream process, such as synthetic fuel production.
    To accomplish this, a dummy technology is linked to the CO2-producing
    technology, converting the emissions activity into a physical commodity
    amount as follows:

    .. math::
       :label: LinkedEmissionsTech

         - \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o} \cdot EAC_{r, e, i, t, v, o}
         = \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}

        \forall \{r, p, s, d, t, v, e\} \in \Theta_{\text{linked_techs}}

    The relationship between the primary and linked technologies is given
    in the :code:`linked_techs` table. Note that the primary and linked
    technologies cannot be part of the :code:`tech_annual` set. It is implicit that
    the primary region corresponds to the linked technology as well. The lifetimes
    of the primary and linked technologies should be specified and identical.
    """

    if t in model.tech_annual:
        primary_flow = quicksum(
            (
                value(model.demand_specific_distribution[r, p, s, d, S_o])
                if S_o in model.commodity_demand
                else value(model.segment_fraction[p, s, d])
            )
            * model.v_flow_out_annual[r, p, S_i, t, v, S_o]
            * value(model.emission_activity[r, e, S_i, t, v, S_o])
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
    else:
        primary_flow = quicksum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
            * value(model.emission_activity[r, e, S_i, t, v, S_o])
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )

    linked_t = value(model.linked_techs[r, t, e])

    # linked_flow = sum(
    #     M.v_flow_out[r, p, s, d, S_i, linked_t, v, S_o]
    #     for S_i in M.processInputs[r, p, linked_t, v]
    #     for S_o in M.process_outputs_by_input[r, p, linked_t, v, S_i]
    # )

    if linked_t in model.tech_annual:
        linked_flow = quicksum(
            (
                value(model.demand_specific_distribution[r, p, s, d, S_o])
                if S_o in model.commodity_demand
                else value(model.segment_fraction[p, s, d])
            )
            * model.v_flow_out_annual[r, p, S_i, linked_t, v, S_o]
            for S_i in model.process_inputs[r, p, linked_t, v]
            for S_o in model.process_outputs_by_input[r, p, linked_t, v, S_i]
        )
    else:
        linked_flow = quicksum(
            model.v_flow_out[r, p, s, d, S_i, linked_t, v, S_o]
            for S_i in model.process_inputs[r, p, linked_t, v]
            for S_o in model.process_outputs_by_input[r, p, linked_t, v, S_i]
        )

    return -primary_flow == linked_flow
