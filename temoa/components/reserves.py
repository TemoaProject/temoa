from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import Constraint, value

from .utils import get_variable_efficiency

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


def ReserveMarginIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d)
        for r in M.PlanningReserveMargin.sparse_iterkeys()
        for p in M.time_optimize
        if (r, p) in M.processReservePeriods
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return indices


def ReserveMarginDynamic(M: 'TemoaModel', r, p, s, d):
    r"""
    A dynamic alternative to the traditional, static reserve margin constraint. Capacity values
    are calculated from availability of generation in each hour—like an operating reserve margin—\
    accounting for a capacity derate factor subtracting, for example, forced outage due to icing.

    .. math::
        :label: reserve_margin_dynamic

            &\sum_{t \in T^{res} \setminus T^{x} \setminus T^s,\ V} CFP_{r,p,s^*,d^*,t,v}\
                \cdot RCD_{r,p,s^*,t,v}\
                \cdot \mathbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*}\
                \cdot C2A_{r,t} \\
            &+ \sum_{t \in T^{res} \cap T^{x} \setminus T^s,\ V} CFP_{r_i - r, p, s^*, d^*, t, v}\
                \cdot RCD_{r_i - r, p, s^*, t, v}\
                \cdot \mathbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*}\
                \cdot C2A_{r_i - r, t} \\
            &- \sum_{t \in T^{res} \cap T^{x} \setminus T^s,\ V} CFP_{r - r_i, p, s^*, d^*, t, v}\
                \cdot RCD_{r - r_i, p, s^*, t, v}\
                \cdot \mathbf{CAPAVL}_{p,t}\
                \cdot SEG_{s^*,d^*} \cdot C2A_{r - r_i, t} \\
            &+ \sum_{t \in (T^s \cap T^{res}), V, I, O} \
                \left(\
                \mathbf{FO}_{r,p,s,d,i,t,v,o} - \mathbf{FI}_{r,p,s,d,i,t,v,o}\
                \right)\
                \cdot RCD_{r,p,s,t,v} \\
            &\geq\
                \left[\
                \sum_{t \in T^{res} \setminus T^{x}, V, I, O}\
                \mathbf{FO}_{r, p, s, d, i, t, v, o}\
                \right. \\
            &+ \sum_{t \in T^{res} \cap T^{x}, V, I, O} \
                \mathbf{FO}_{r_i - r, p, s, d, i, t, v, o} \\
            &- \sum_{t \in T^{res} \cap T^{x}, V, I, O} \
                \mathbf{FI}_{r - r_i, p, s, d, i, t, v, o} \\
            &- \left. \sum_{t \in T^{res} \cap T^{s}, V, I, O} \
                \mathbf{FI}_{r, p, s, d, i, t, v, o} \right] \cdot (1 + PRM_r) \\
            \\
            &\qquad \qquad \forall \{r, p, s, d\} \in \
            \Theta_{\text{ReserveMargin}} \text{ and } \forall r_i \in R
    """
    if (not M.tech_reserve) or (
        (r, p) not in M.processReservePeriods
    ):  # If reserve set empty or if r,p not in M.processReservePeriod, skip the constraint
        return Constraint.Skip

    # Everything but storage and exchange techs
    # Derated available generation
    available = sum(
        M.V_Capacity[r, p, t, v]
        * value(M.ReserveCapacityDerate[r, p, s, t, v])
        * value(M.CapacityFactorProcess[r, p, s, d, t, v])
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        for (t, v) in M.processReservePeriods[r, p]
        if t not in M.tech_uncap and t not in M.tech_storage
    )

    # Storage
    # Derated net output flow
    available += sum(
        M.V_FlowOut[r, p, s, d, i, t, v, o] * value(M.ReserveCapacityDerate[r, p, s, t, v])
        for (t, v) in M.processReservePeriods[r, p]
        if t in M.tech_storage
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
    )
    available -= sum(
        M.V_FlowIn[r, p, s, d, i, t, v, o] * value(M.ReserveCapacityDerate[r, p, s, t, v])
        for (t, v) in M.processReservePeriods[r, p]
        if t in M.tech_storage
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
    )

    # The above code does not consider exchange techs, e.g. electricity
    # transmission between two distinct regions.
    # We take exchange takes into account below.
    # Note that a single exchange tech linking regions Ri and Rj is twice
    # defined: once for region "Ri-Rj" and once for region "Rj-Ri".

    # First, determine the amount of firm capacity each exchange tech
    # contributes.
    for r1r2 in M.regionalIndices:
        if '-' not in r1r2:
            continue
        if (r1r2, p) not in M.processReservePeriods:  # ensure r1r2 is a valid reserve provider in p
            continue
        r1, r2 = r1r2.split('-')

        # Only consider the capacity of technologies that import to
        # the region in question -- i.e. for cases where r2 == r.
        if r2 != r:
            continue

        # add the available output of the exchange tech.
        available += sum(
            M.V_Capacity[r1r2, p, t, v]
            * value(M.ReserveCapacityDerate[r, p, s, t, v])
            * value(M.CapacityFactorProcess[r, p, s, d, t, v])
            * value(M.CapacityToActivity[r1r2, t])
            * value(M.SegFrac[p, s, d])
            for (t, v) in M.processReservePeriods[r1r2, p]
            for t in M.tech_reserve
        )

    return available


def ReserveMarginStatic(M: 'TemoaModel', r, p, s, d):
    r"""

    During each period :math:`p`, the sum of capacity values of all reserve
    technologies :math:`\sum_{t \in T^{res}} \textbf{CAPAVL}_{r,p,t}`, which are
    defined in the set :math:`\textbf{T}^{res}`, should exceed the peak load by
    :math:`PRM`, the regional reserve margin. Note that the reserve
    margin is expressed in percentage of the peak load. Generally speaking, in
    a database we may not know the peak demand before running the model, therefore,
    we write this equation for all the time-slices defined in the database in each region.
    Each generator is allowed to contribute its available capacity times a pre-defined
    capacity credit, :math:`CC_{t,r}`

    .. math::
        :label: reserve_margin_static

            &\sum_{t \in T^{res} \setminus T^{x}} {CC_{t,r} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r,t} }\\
            &+ \sum_{t \in T^{res} \cap T^{x}} {CC_{t,r_i-r} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r_i-r,t} }\\
            &- \sum_{t \in T^{res} \cap T^{x}} {CC_{t,r-r_i} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r-r_i,t} }\\
            &\geq \left [ \sum_{ t \in T^{res} \setminus T^{x},V,I,O } \textbf{FO}_{r, p, s, d, i, t, v, o}\right.\\
            &+ \sum_{ t \in T^{res} \cap T^{x},V,I,O } \textbf{FO}_{r_i-r, p, s, d, i, t, v, o}\\
            &- \sum_{ t \in T^{res} \cap T^{x},V,I,O } \textbf{FI}_{r-r_i, p, s, d, i, t, v, o}\\
            &- \left.\sum_{ t \in T^{res} \cap T^{s},V,I,O } \textbf{FI}_{r, p, s, d, i, t, v, o}  \right]  \cdot (1 + PRM_r)\\

            \\
            &\qquad\qquad\forall \{r, p, s, d\} \in \Theta_{\text{ReserveMargin}} \text{and} \forall r_i \in R
    """
    if (not M.tech_reserve) or (
        (r, p) not in M.processReservePeriods
    ):  # If reserve set empty or if r,p not in M.processReservePeriod, skip the constraint
        return Constraint.Skip

    available = sum(
        value(M.CapacityCredit[r, p, t, v])
        * M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        for (t, v) in M.processReservePeriods[r, p]
        if t not in M.tech_uncap
    )

    # The above code does not consider exchange techs, e.g. electricity
    # transmission between two distinct regions.
    # We take exchange takes into account below.
    # Note that a single exchange tech linking regions Ri and Rj is twice
    # defined: once for region "Ri-Rj" and once for region "Rj-Ri".

    # First, determine the amount of firm capacity each exchange tech
    # contributes.
    for r1r2 in M.regionalIndices:
        if '-' not in r1r2:
            continue
        if (r1r2, p) not in M.processReservePeriods:  # ensure r1r2 is a valid reserve provider in p
            continue
        r1, r2 = r1r2.split('-')

        # Only consider the capacity of technologies that import to
        # the region in question -- i.e. for cases where r2 == r.
        if r2 != r:
            continue

        # add the available capacity of the exchange tech.
        available += sum(
            value(M.CapacityCredit[r1r2, p, t, v])
            * M.V_Capacity[r1r2, p, t, v]
            * value(M.CapacityToActivity[r1r2, t])
            * value(M.SegFrac[p, s, d])
            for (t, v) in M.processReservePeriods[r1r2, p]
            for t in M.tech_reserve
        )

    return available


def ReserveMargin_Constraint(M: 'TemoaModel', r, p, s, d):
    # Get available generation in this time slice depending on method specified in config file
    match M.ReserveMarginMethod.first():
        case 'static':
            available = ReserveMarginStatic(M, r, p, s, d)
        case 'dynamic':
            available = ReserveMarginDynamic(M, r, p, s, d)
        case _:
            msg = f"Invalid reserve margin parameter '{M.ReserveMarginMethod.first()}'. Check the config file."
            logger.error(msg)
            raise ValueError(msg)

    # In most Temoa input databases, demand is endogenous, so we use electricity
    # generation instead as a proxy for electricity demand.
    # Non-annual generation
    total_generation = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
        if t not in M.tech_annual
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.processOutputsByInput[r, p, t, S_v, S_i]
    )

    # Generators might serve demands directly
    # Annual generation
    total_generation += sum(
        (
            value(M.DemandSpecificDistribution[r, p, s, d, S_o])
            if S_o in M.commodity_demand
            else value(M.SegFrac[p, s, d])
        )
        * M.V_FlowOutAnnual[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
        if t in M.tech_annual
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.processOutputsByInput[r, p, t, S_v, S_i]
    )

    # We must take into account flows into storage technologies.
    # Flows into storage technologies need to be subtracted from the
    # load calculation.
    total_generation -= sum(
        M.V_FlowIn[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
        if t in M.tech_storage
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.processOutputsByInput[r, p, t, S_v, S_i]
    )

    # Electricity imports and exports via exchange techs are accounted
    # for below:
    for r1r2 in M.regionalIndices:  # ensure the region is of the form r1-r2
        if '-' not in r1r2:
            continue
        if (r1r2, p) not in M.processReservePeriods:  # ensure r1r2 is a valid reserve provider in p
            continue
        r1, r2 = r1r2.split('-')
        # First, determine the exports, and subtract this value from the
        # total generation.
        if r1 == r:
            total_generation -= sum(
                M.V_FlowOut[r1r2, p, s, d, S_i, t, S_v, S_o]
                / get_variable_efficiency(M, r1r2, p, s, d, S_i, t, S_v, S_o)
                for (t, S_v) in M.processReservePeriods[r1r2, p]
                for S_i in M.processInputs[r1r2, p, t, S_v]
                for S_o in M.processOutputsByInput[r1r2, p, t, S_v, S_i]
            )
        # Second, determine the imports, and add this value from the
        # total generation.
        elif r2 == r:
            total_generation += sum(
                M.V_FlowOut[r1r2, p, s, d, S_i, t, S_v, S_o]
                for (t, S_v) in M.processReservePeriods[r1r2, p]
                for S_i in M.processInputs[r1r2, p, t, S_v]
                for S_o in M.processOutputsByInput[r1r2, p, t, S_v, S_i]
            )

    requirement = total_generation * (1 + value(M.PlanningReserveMargin[r]))
    return available >= requirement
