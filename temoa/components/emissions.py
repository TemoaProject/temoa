# temoa/components/emissions.py
"""
Defines the components of the Temoa model related to emissions accounting.

This module is responsible for:
-  Defining index sets for emission-related parameters and constraints.
-  Defining the constraint rule for 'linked technologies', a special case where
    an emission commodity (e.g., captured CO2) is also treated as a physical
    input to a downstream process (e.g., synthetic fuel production).
"""

from typing import TYPE_CHECKING

from pyomo.core import Expression
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def EmissionActivityIndices(M: 'TemoaModel') -> set[tuple[str, str, str, str, int, str]]:
    indices = {
        (r, e, i, t, v, o)
        for r, i, t, v, o in M.Efficiency.sparse_iterkeys()
        for e in M.commodity_emissions
        if r in M.regions  # omit any exchange/groups
    }

    return indices


def LinkedTechConstraintIndices(M: 'TemoaModel') -> set[tuple[str, int, str, str, str, int, str]]:
    linkedtech_indices = {
        (r, p, s, d, t, v, e)
        for r, t, e in M.LinkedTechs.sparse_iterkeys()
        for p in M.time_optimize
        if (r, p, t) in M.processVintages
        for v in M.processVintages[r, p, t]
        if M.activeActivity_rptv and (r, p, t, v) in M.activeActivity_rptv
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    }

    return linkedtech_indices


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def LinkedEmissionsTech_Constraint(
    M: 'TemoaModel', r: str, p: int, s: str, d: str, t: str, v: int, e: str
) -> Expression:
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

        \forall \{r, p, s, d, t, v, e\} \in \Theta_{\text{LinkedTechs}}

    The relationship between the primary and linked technologies is given
    in the :code:`LinkedTechs` table. Note that the primary and linked
    technologies cannot be part of the :code:`tech_annual` set. It is implicit that
    the primary region corresponds to the linked technology as well. The lifetimes
    of the primary and linked technologies should be specified and identical.
    """

    if t in M.tech_annual:
        primary_flow = sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
            * value(M.EmissionActivity[r, e, S_i, t, v, S_o])
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
    else:
        primary_flow = sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            * value(M.EmissionActivity[r, e, S_i, t, v, S_o])
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )

    linked_t = M.LinkedTechs[r, t, e]

    # linked_flow = sum(
    #     M.V_FlowOut[r, p, s, d, S_i, linked_t, v, S_o]
    #     for S_i in M.processInputs[r, p, linked_t, v]
    #     for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
    # )

    if linked_t in M.tech_annual:
        linked_flow = sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, S_i, linked_t, v, S_o]
            for S_i in M.processInputs[r, p, linked_t, v]
            for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
        )
    else:
        linked_flow = sum(
            M.V_FlowOut[r, p, s, d, S_i, linked_t, v, S_o]
            for S_i in M.processInputs[r, p, linked_t, v]
            for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
        )

    return -primary_flow == linked_flow
