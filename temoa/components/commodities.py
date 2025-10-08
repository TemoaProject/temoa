import sys
from itertools import product as cross_product
from logging import getLogger
from operator import itemgetter as iget
from typing import TYPE_CHECKING
from pyomo.environ import Constraint, value

from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

from .utils import get_variable_efficiency

logger = getLogger(name=__name__)


def CommodityBalanceConstraintErrorCheck(supplied, demanded, r, p, s, d, c):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) or isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            'Unable to balance commodity {} in ({}, {}, {}, {}).\n'
            'No flows on one side of constraint expression:\n'
            '   {}\n'
            'Possible reasons:\n'
            " - Is there a missing period in set 'time_future'?\n"
            " - Is there a missing tech in set 'tech_resource'?\n"
            " - Is there a missing tech in set 'tech_production'?\n"
            " - Is there a missing commodity in set 'commodity_physical'?\n"
            ' - Are there missing entries in the Efficiency table?\n'
            ' - Does a process need a longer Lifetime?'
        )
        logger.error(msg.format(c, r, p, s, d, expr))
        raise Exception(msg.format(c, r, p, s, d, expr))


def AnnualCommodityBalanceConstraintErrorCheck(supplied, demanded, r, p, c):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) or isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            'Unable to balance annual commodity {} in ({}, {}).\n'
            'No flows on one side of constraint expression:\n'
            '   {}\n'
            'Possible reasons:\n'
            " - Is there a missing period in set 'time_future'?\n"
            " - Is there a missing tech in set 'tech_resource'?\n"
            " - Is there a missing tech in set 'tech_production'?\n"
            " - Is there a missing commodity in set 'commodity_physical'?\n"
            ' - Are there missing entries in the Efficiency table?\n'
            ' - Does a process need a longer Lifetime?'
        )
        logger.error(msg.format(c, r, p, expr))
        raise Exception(msg.format(c, r, p, expr))


def DemandConstraintErrorCheck(supply, r, p, dem):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem
    if isinstance(supply, int):
        msg = (
            "Error: Demand '{}' for ({}, {}) unable to be met by any "
            'technology.\n\tPossible reasons:\n'
            ' - Is the Efficiency parameter missing an entry for this demand?\n'
            ' - Does a tech that satisfies this demand need a longer '
            'Lifetime?\n'
        )
        logger.error(msg.format(dem, r, p))
        raise Exception(msg.format(dem, r, p))


def DemandActivityConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v, dem)
        for r, p, dem in M.DemandConstraint_rpc
        for t, v in M.commodityUStreamProcess[r, p, dem]
        if t not in M.tech_annual
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    return indices


def CreateDemands(M: 'TemoaModel'):
    """
    Steps to create the demand distributions
    1. Use Demand keys to ensure that all demands in commodity_demand are used
    2. Find any slices not set in DemandDefaultDistribution, and set them based
    on the associated SegFrac slice.
    3. Validate that the DemandDefaultDistribution sums to 1.
    4. Find any per-demand DemandSpecificDistribution values not set, and set
    them from DemandDefaultDistribution.  Note that this only sets a
    distribution for an end-use demand if the user has *not* specified _any_
    anything for that end-use demand.  Thus, it is up to the user to fully
    specify the distribution, or not.  No in-between.
     5. Validate that the per-demand distributions sum to 1.
    """
    logger.debug('Started creating demand distributions in CreateDemands()')

    # Step 0: some setup for a couple of reusable items
    # Get the nth element from the tuple (r, p, s, d, dem)
    # So we only have to update these indices in one place if they change
    DSD_region = iget(0)
    DSD_period = iget(1)
    DSD_dem = iget(4)

    # Step 1: Check if any demand commodities are going unused
    used_dems = set(dem for r, p, dem in M.Demand.sparse_iterkeys())
    unused_dems = sorted(M.commodity_demand.difference(used_dems))
    if unused_dems:
        for dem in unused_dems:
            msg = "Warning: Demand '{}' is unused\n"
            logger.warning(msg.format(dem))
            sys.stderr.write(msg.format(dem))

    # devnote: DDD just clones SegFrac. Unless we want to specify it in the database,
    #          makes sense to just use SegFrac directly
    # Step 2: Build the demand default distribution (= segfrac)
    # DDD = M.DemandDefaultDistribution  # Shorter, for us lazy programmer types
    # unset_defaults = set(M.SegFrac.sparse_iterkeys())
    # unset_defaults.difference_update(DDD.sparse_iterkeys())
    # if unset_defaults:
    # Some hackery because Pyomo thinks that this Param is constructed.
    # However, in our view, it is not yet, because we're specifically
    # targeting values that have not yet been constructed, that we know are
    # valid, and that we will need.
    # DDD._constructed = False
    # for tslice in unset_defaults:
    #     DDD[tslice] = M.SegFrac[tslice]  # DDD._constructed = True

    # Step 3: Check that DDD sums to 1
    # devnote: this seems redundant to the SegFrac sum to 1 check.
    # total = sum(i for i in DDD.values())
    # if abs(value(total) - 1.0) > 0.001:
    #     # We can't explicitly test for "!= 1.0" because of incremental rounding
    #     # errors associated with the specification of demand shares by time slice,
    #     # but we check to make sure it is within the specified tolerance.

    #     key_padding = max(map(get_str_padding, DDD.sparse_iterkeys()))

    #     fmt = '%%-%ds = %%s' % key_padding
    #     # Works out to something like "%-25s = %s"

    #     items = sorted(DDD.items())
    #     items = '\n   '.join(fmt % (str(k), v) for k, v in items)

    #     msg = (
    #         'The values of the DemandDefaultDistribution parameter do not '
    #         'sum to 1.  The DemandDefaultDistribution specifies how end-use '
    #         'demands are distributed among the time slices (i.e., time_season, '
    #         'time_of_day), so together, the data must total to 1.  Current '
    #         'values:\n   {}\n\tsum = {}'
    #     )
    #     logger.error(msg.format(items, total))
    #     raise ValueError(msg.format(items, total))

    # Step 4: Fill out demand specific distribution table and check sums to 1 by region and demand
    DSD = M.DemandSpecificDistribution

    demands_specified = set(map(DSD_dem, (i for i in DSD.sparse_iterkeys())))
    unset_demand_distributions = used_dems.difference(
        demands_specified
    )  # the demands not mentioned in DSD *at all*

    if unset_demand_distributions:
        for p in M.time_optimize:
            unset_distributions = set(
                cross_product(
                    M.regions, (p,), M.TimeSeason[p], M.time_of_day, unset_demand_distributions
                )
            )
            for r, p, s, d, dem in unset_distributions:
                DSD[r, p, s, d, dem] = value(M.SegFrac[p, s, d])  # DSD._constructed = True

    # Step 5: A final "sum to 1" check for all DSD members (which now should be everything)
    #         Also check that all keys are made...  The demand distro should be supported
    #         by the full set of (r, p, dem) keys because it is an equality constraint
    #         and we need to ensure even the zeros are passed in
    used_rp_dems = set((r, p, dem) for r, p, dem in M.Demand.sparse_iterkeys())
    for r, p, dem in used_rp_dems:
        expected_key_length = len(M.TimeSeason[p]) * len(M.time_of_day)
        keys = [
            k
            for k in DSD.sparse_iterkeys()
            if DSD_region(k) == r and DSD_period(k) == p and DSD_dem(k) == dem
        ]
        if len(keys) != expected_key_length:
            # this could be very slow but only calls when there's a problem
            missing = set(
                (s, d)
                for s in M.TimeSeason[p]
                for d in M.time_of_day
                if (r, p, s, d, dem) not in keys
            )
            logger.info(
                'Missing some time slices for Demand Specific Distribution %s: %s',
                (r, p, dem),
                missing,
            )
        total = sum(value(DSD[i]) for i in keys)
        if abs(value(total) - 1.0) > 0.001:
            # We can't explicitly test for "!= 1.0" because of incremental rounding
            # errors associated with the specification of demand shares by time slice,
            # but we check to make sure it is within the specified tolerance.
            def get_str_padding(obj):
                return len(str(obj))

            key_padding = max(map(get_str_padding, keys))

            fmt = '%%-%ds = %%s' % key_padding
            # Works out to something like "%-25s = %s"

            items = sorted((k, value(DSD[k])) for k in keys)
            items = '\n   '.join(fmt % (str(k), v) for k, v in items)

            msg = (
                'The values of the DemandSpecificDistribution parameter do not '
                'sum to 1 for {}. The DemandSpecificDistribution specifies how end-use '
                'demands are distributed per time-slice (i.e., time_season, '
                'time_of_day). Within each region, period, end-use demand, then, the distribution '
                'must total to 1.\n\n Demand-specific distribution in error: '
                ' \n   {}\n\tsum = {}'
            )
            logger.error(msg.format((r, p, dem), items, total))
            raise ValueError(msg.format((r, p, dem), items, total))

    logger.debug('Finished creating demand distributions')


def CommodityBalanceConstraintIndices(M: 'TemoaModel'):
    # Generate indices only for those commodities that are produced by
    # technologies with varying output at the time slice level.
    indices = set(
        (r, p, s, d, c)
        for r, p, c in M.commodityBalance_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in M.regions  # this line ensures only the regions are included.
        and c not in M.commodity_annual
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return indices


def AnnualCommodityBalanceConstraintIndices(M: 'TemoaModel'):
    # Generate indices only for those commodities that are produced by
    # technologies with constant annual output.
    indices = set(
        (r, p, c)
        for r, p, c in M.commodityBalance_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in M.regions  # this line ensures only the regions are included.
        and c in M.commodity_annual
    )

    return indices


def Demand_Constraint(M: 'TemoaModel', r, p, dem):
    r"""

    The Demand constraint drives the model.  This constraint ensures that supply at
    least meets the demand specified by the Demand parameter in all periods and
    slices, by ensuring that the sum of all the demand output commodity (:math:`c`)
    generated by both commodity flow at the time slice level (:math:`\textbf{FO}`) and
    the annual level (:math:`\textbf{FOA}`) must meet the modeler-specified demand
    in each time slice.

    .. math::
       :label: Demand

           \sum_{I, T-T^{a}, V} \textbf{FO}_{r, p, s, d, i, t \not \in T^{a}, v, dem} +
           SEG_{s,d} \cdot  \sum_{I, T^{a}, V} \textbf{FOA}_{r, p, i, t \in T^{a}, v, dem}
           =
           {DEM}_{r, p, dem} \cdot {DSD}_{r, s, d, dem}

    Note that the validity of this constraint relies on the fact that the
    :math:`C^d` set is distinct from both :math:`C^e` and :math:`C^p`. In other
    words, an end-use demand must only be an end-use demand.  Note that if an output
    could satisfy both an end-use and internal system demand, then the output from
    :math:`\textbf{FO}` and :math:`\textbf{FOA}` would be double counted."""

    # All demand techs are annual now
    # supply = sum(
    #     M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, dem]
    #     for S_t, S_v in M.commodityUStreamProcess[r, p, dem]
    #     if S_t not in M.tech_annual
    #     for S_i in M.processInputsByOutput[r, p, S_t, S_v, dem]
    # )

    supply_annual = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, dem]
        for S_t, S_v in M.commodityUStreamProcess[r, p, dem]
        for S_i in M.processInputsByOutput[r, p, S_t, S_v, dem]
    )

    DemandConstraintErrorCheck(supply_annual, r, p, dem)

    expr = supply_annual == value(M.Demand[r, p, dem])

    return expr


# devnote: no longer needed
def DemandActivity_Constraint(M: 'TemoaModel', r, p, s, d, t, v, dem):
    r"""

    For end-use demands, it is unreasonable to let the model arbitrarily shift the
    use of demand technologies across time slices. For instance, if household A buys
    a natural gas furnace while household B buys an electric furnace, then both units
    should be used throughout the year.  Without this constraint, the model might choose
    to only use the electric furnace during the day, and the natural gas furnace during the
    night.

    This constraint ensures that the ratio of a process activity to demand is
    constant for all time slices.  Note that if a demand is not specified in a given
    time slice, or is zero, then this constraint will not be considered for that
    slice and demand.  This is transparently handled by the :math:`\Theta` superset.

    .. math::
       :label: DemandActivity

          DEM_{r, p, s, d, dem} \cdot \sum_{I} \textbf{FO}_{r, p, s_0, d_0, i, t \not \in T^{a}, v, dem}
       =
          DEM_{r, p, s_0, d_0, dem} \cdot \sum_{I} \textbf{FO}_{r, p, s, d, i, t \not \in T^{a}, v, dem}

       \\
       \forall \{r, p, s, d, t, v, dem, s_0, d_0\} \in \Theta_{\text{DemandActivity}}

    Note that this constraint is only applied to the demand commodities with diurnal
    variations, and therefore the equation above only includes :math:`\textbf{FO}`
    and not  :math:`\textbf{FOA}`
    """

    activity = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, dem] for S_i in M.processInputsByOutput[r, p, t, v, dem]
    )

    annual_activity = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, dem] for S_i in M.processInputsByOutput[r, p, t, v, dem]
    )

    expr = annual_activity * value(M.DemandSpecificDistribution[r, p, s, d, dem]) == activity
    return expr


def CommodityBalance_Constraint(M: 'TemoaModel', r, p, s, d, c):
    r"""
    Where the Demand constraint :eq:`Demand` ensures that end-use demands are met,
    the CommodityBalance constraint ensures that the endogenous system demands are
    met.  This constraint requires the total production of a given commodity
    to equal the amount consumed, thus ensuring an energy balance at the system
    level. In this most general form of the constraint, the energy commodity being
    balanced has variable production at the time slice level. The energy commodity
    can then be consumed by three types of processes: storage technologies, non-storage
    technologies with output that varies at the time slice level, and non-storage
    technologies with constant annual output.

    Separate expressions are required in order to account for the consumption of
    commodity :math:`c` by downstream processes. For the commodity flow into storage
    technologies, we use :math:`\textbf{FI}_{r, p, s, d, i, t, v, c}`. Note that the FlowIn
    variable is defined only for storage technologies, and is required because storage
    technologies balance production and consumption across time slices rather than
    within a single time slice. For commodity flows into non-storage processes with time
    varying output, we use :math:`\textbf{FO}_{r, p, s, d, i, t, v, c}/EFF_{r, i,t,v,o}`.
    The division by :math:`EFF_{r, c,t,v,o}` is applied to the output flows that consume
    commodity :math:`c` to determine input flows. Finally, we need to account
    for the consumption of commodity :math:`c` by the processes in
    :code:`tech_annual`. Since the commodity flow of these processes is on an
    annual basis, we use :math:`SEG_{s,d}` to calculate the consumption of
    commodity :math:`c` in time-slice :math:`(s,d)` from the annual flows.
    Formulating an expression for the production of commodity :math:`c` is
    more straightforward, and is simply calculated by
    :math:`\textbf{FO}_{r, p, s, d, i, t, v, c}`.

    In some cases, the overproduction of a commodity may be required, such
    that the supply exceeds the endogenous demand. Refineries represent a
    common example, where the share of different refined products are governed
    by TechOutputSplit, but total production is driven by a particular commodity
    like gasoline. Such a situation can result in the overproduction of other
    refined products, such as diesel or kerosene. In such cases, we need to
    track the excess production of these commodities. To do so, the technology
    producing the excess commodity should be added to the :code:`tech_flex` set.
    This flexible technology designation will activate a slack variable
    (:math:`\textbf{FLX}_{r, p, s, d, i, t, v, c}`) representing
    the excess production in the :code:`CommodityBalanceAnnual_Constraint`. Note
    that the :code:`tech_flex` set is different from :code:`tech_curtailment` set;
    the latter is technology- rather than commodity-focused and is used in the
    :code:`Capacity_Constraint` to track output that is used to produce useful
    output and the amount curtailed, and to ensure that the installed capacity
    covers both. Alternatively, the commodity can be added to the
    :code:`commodity_waste` set, for which this equality constraint becomes an
    inequality constraint, allowing production to exceed consumption for a single
    commodity.

    This constraint also accounts for imports and exports between regions
    when solving multi-regional systems. The import (:math:`\textbf{FIM}`) and export
    (:math:`\textbf{FEX}`) variables are created on-the-fly by summing the
    :math:`\textbf{FO}` variables over the appropriate import and export regions,
    respectively, which are defined in :code:`temoa_initialize.py` by parsing the
    :code:`tech_exchange` processes.

    Consumption of the commodity by construction inputs is annualised using the period
    length. Production of the commodity by end-of-life outputs uses the AnnualRetirement
    variable, which is already annualised.

    Finally, for annual commodities, AnnualCommodityBalance is used which balances
    the sum of flows over each year.

    *process outputs + imports + end of life outputs = process inputs + construction inputs + exports + flex waste*

    .. math::
       :label: CommodityBalance

            \begin{aligned}
            &\sum_{I, t \notin T^a, V} \mathbf{FO}_{r, p, s, d, i, t, v, c}
            && \text{(processes outputting commodity)} \\
            &+ SEG_{s,d} \cdot \sum_{I, t \in T^a, V} \frac{\mathbf{FOA}_{r, p, i, t, v, c}}{EFF_{r, i, t, v, c}}
            && \text{(annual processes outputting commodity)} \\
            &+ \sum_{\text{reg} \neq r, I, t \in T^x, V} \mathbf{FIM}_{r - \text{reg}, p, s, d, i, t, v, c}
            && \text{(inter-regional imports of commodity)} \\
            &+ SEG_{s,d} \sum_{T, V} \left ( EOLO_{r, t, v, c} \cdot \textbf{ART}_{r, p, t, v} \right )
            && \text{(end-of-life outputs of commodity)} \\
            &\begin{cases}
            &= \text{if } c \notin C^w \\
            &\geq \text{if } c \in C^w \end{cases} \\
            &\sum_{t \in T^s, V, O} \mathbf{FIS}_{r, p, s, d, c, t, v, o}
            && \text{(commodity stored)} \\
            &+ \sum_{t \notin T^s, V, O} \frac{\mathbf{FO}_{r, p, s, d, c, t, v, o}}{EFF_{r, c, t, v, o}}
            && \text{(commodity consumed by processes)} \\
            &+ SEG_{s,d} \cdot \sum_{t \in T^a, V, O} \frac{\mathbf{FOA}_{r, p, c, t, v, o}}{EFF_{r, c, t, v, o}}
            && \text{(commodity consumed by annual processes)} \\
            &+ \sum_{\text{reg} \neq r, t \in T^x, V, O} \mathbf{FEX}_{r - \text{reg}, p, s, d, c, t, v, o}
            && \text{(inter-regional exports of commodity)} \\
            &+ \sum_{I, t \in T^f, V} \mathbf{FLX}_{r, p, s, d, i, t, v, c}
            && \text{(flex wastes of commodity)} \\
            &+ SEG_{s,d} \cdot \sum_{T, V} \left ( CON_{r, c, t, v} \cdot \frac{\textbf{NCAP}_{r, t, v}}{LEN_p} \right )
            && \text{(consumed annually by construction inputs)}
            \end{aligned}

            \qquad \forall \{r, p, s, d, c\} \in \Theta_{\text{CommodityBalance}}

    """

    produced = 0
    consumed = 0

    if (r, p, c) in M.commodityDStreamProcess:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            M.V_FlowIn[r, p, s, d, c, S_t, S_v, S_o]
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_storage
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        # Into flows
        consumed += sum(
            M.V_FlowOut[r, p, s, d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r, p, s, d, c, S_t, S_v, S_o)
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t not in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        # Into annual flows
        consumed += sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r, p, s, d, c, S_t, S_v, S_o)
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

    if (r, p, c) in M.capacityConsumptionTechs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += (
            value(M.SegFrac[p, s, d])
            * sum(
                value(M.ConstructionInput[r, c, S_t, p]) * M.V_NewCapacity[r, S_t, p]
                for S_t in M.capacityConsumptionTechs[r, p, c]
            )
            / M.PeriodLength[p]
        )

    if (r, p, c) in M.commodityUStreamProcess:
        # From flows including output from storage
        produced += sum(
            M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t not in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        # From annual flows
        produced += value(M.SegFrac[p, s, d]) * sum(
            M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        if c in M.commodity_flex:
            # Wasted by flex flows
            consumed += sum(
                M.V_Flex[r, p, s, d, S_i, S_t, S_v, c]
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t not in M.tech_annual and S_t in M.tech_flex
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )
            # Wasted by annual flex flows
            consumed += value(M.SegFrac[p, s, d]) * sum(
                M.V_FlexAnnual[r, p, S_i, S_t, S_v, c]
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t in M.tech_annual and S_t in M.tech_flex
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )

    if (r, p, c) in M.retirementProductionProcesses:
        # Produced by retiring capacity
        # Assume evenly distributed over a year
        produced += value(M.SegFrac[p, s, d]) * sum(
            value(M.EndOfLifeOutput[r, S_t, S_v, c]) * M.V_AnnualRetirement[r, p, S_t, S_v]
            for S_t, S_v in M.retirementProductionProcesses[r, p, c]
        )

    # export of commodity c from region r to other regions
    if (r, p, c) in M.exportRegions:
        consumed += sum(
            M.V_FlowOut[r + '-' + reg, p, s, d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r + '-' + reg, p, s, d, c, S_t, S_v, S_o)
            for reg, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        consumed += sum(
            value(M.SegFrac[p, s, d])
            * M.V_FlowOutAnnual[r + '-' + reg, p, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r + '-' + reg, p, s, d, c, S_t, S_v, S_o)
            for reg, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t in M.tech_annual
        )

    # import of commodity c from other regions into region r
    if (r, p, c) in M.importRegions:
        produced += sum(
            M.V_FlowOut[reg + '-' + r, p, s, d, S_i, S_t, S_v, c]
            for reg, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        produced += sum(
            value(M.SegFrac[p, s, d]) * M.V_FlowOutAnnual[reg + '-' + r, p, S_i, S_t, S_v, c]
            for reg, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t in M.tech_annual
        )

    CommodityBalanceConstraintErrorCheck(
        produced,
        consumed,
        r,
        p,
        s,
        d,
        c,
    )

    if c in M.commodity_waste:
        expr = produced >= consumed
    else:
        expr = produced == consumed

    return expr


def AnnualCommodityBalance_Constraint(M: 'TemoaModel', r, p, c):
    r"""
    Similar to CommodityBalance_Constraint but only balances the supply and demand of the commodity
    at the period level, summing all flows over the period but allowing imbalances at the time slice
    or seasonal level. Applies only to commodities in the :code:`commodity_annual` set.
    """

    produced = 0
    consumed = 0

    if (r, p, c) in M.commodityDStreamProcess:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            M.V_FlowIn[r, p, S_s, S_d, c, S_t, S_v, S_o]
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_storage
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        consumed += sum(
            M.V_FlowOut[r, p, S_s, S_d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r, p, S_s, S_d, c, S_t, S_v, S_o)
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t not in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        consumed += sum(
            M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

    if (r, p, c) in M.capacityConsumptionTechs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += (
            sum(
                value(M.ConstructionInput[r, c, S_t, p]) * M.V_NewCapacity[r, S_t, p]
                for S_t in M.capacityConsumptionTechs[r, p, c]
            )
            / M.PeriodLength[p]
        )

    if (r, p, c) in M.commodityUStreamProcess:
        # Includes output from storage
        produced += sum(
            M.V_FlowOut[r, p, S_s, S_d, S_i, S_t, S_v, c]
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t not in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        produced += sum(
            M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        if c in M.commodity_flex:
            consumed += sum(
                M.V_Flex[r, p, S_s, S_d, S_i, S_t, S_v, c]
                for S_s in M.TimeSeason[p]
                for S_d in M.time_of_day
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t not in M.tech_annual and S_t in M.tech_flex
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )
            consumed += sum(
                M.V_FlexAnnual[r, p, S_i, S_t, S_v, c]
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t in M.tech_flex and S_t in M.tech_annual
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )

    if (r, p, c) in M.retirementProductionProcesses:
        # Produced by retiring capacity
        # Assume evenly distributed over a year
        produced += sum(
            value(M.EndOfLifeOutput[r, S_t, S_v, c]) * M.V_AnnualRetirement[r, p, S_t, S_v]
            for S_t, S_v in M.retirementProductionProcesses[r, p, c]
        )

    # export of commodity c from region r to other regions
    if (r, p, c) in M.exportRegions:
        consumed += sum(
            M.V_FlowOut[r + '-' + S_r, p, S_s, S_d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r + '-' + S_r, p, S_s, S_d, c, S_t, S_v, S_o)
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_r, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        consumed += sum(
            M.V_FlowOutAnnual[r + '-' + S_r, p, c, S_t, S_v, S_o]
            / M.Efficiency[r + '-' + S_r, c, S_t, S_v, S_o]
            for S_r, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t in M.tech_annual
        )

    # import of commodity c from other regions into region r
    if (r, p, c) in M.importRegions:
        produced += sum(
            M.V_FlowOut[S_r + '-' + r, p, S_s, S_d, S_i, S_t, S_v, c]
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_r, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        produced += sum(
            M.V_FlowOutAnnual[S_r + '-' + r, p, S_i, S_t, S_v, c]
            for S_r, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t in M.tech_annual
        )

    AnnualCommodityBalanceConstraintErrorCheck(
        produced,
        consumed,
        r,
        p,
        c,
    )

    if c in M.commodity_waste:
        expr = produced >= consumed
    else:
        expr = produced == consumed

    return expr
