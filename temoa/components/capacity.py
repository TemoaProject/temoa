# temoa/components/capacity.py
"""
Defines the capacity-related components of the Temoa model.

This module is responsible for:
-  Defining Pyomo index sets for variables.
-  Defining the rules for all capacity-related constraints, such as capacity
    production limits, retirement accounting, and available capacity aggregation.
-  Pre-calculating sparse index sets for capacity, retirement, and material flows.
"""

from __future__ import annotations

from itertools import product as cross_product
from logging import getLogger
from typing import TYPE_CHECKING

from deprecated import deprecated
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import (
        ExprLike,
        Period,
        Region,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )


logger = getLogger(name=__name__)


# ============================================================================
# HELPER FUNCTIONS AND VALIDATORS
# ============================================================================


def check_capacity_factor_process(model: TemoaModel) -> None:
    count_rptv: dict[tuple[Region, Period, Technology, Vintage], int] = {}
    # Pull capacity_factor_tech by default
    for r, p, _s, _d, t in model.capacity_factor_rpsdt:
        for v in model.process_vintages[r, p, t]:
            model.is_capacity_factor_process[r, p, t, v] = False
            count_rptv[r, p, t, v] = 0

    # Check for bad values and count up the good ones
    for r, p, _s, _d, t, v in model.capacity_factor_process.sparse_iterkeys():
        if v not in model.process_vintages[r, p, t]:
            msg = f'Invalid process {p, v} for {r, t} in capacity_factor_process table'
            logger.error(msg)
            raise ValueError(msg)

        # Good value, pull from capacity_factor_process table
        count_rptv[r, p, t, v] += 1

    # Check if all possible values have been set by process
    # log a warning if some are missing (allowed but maybe accidental)
    for (r, p, t, v), count in count_rptv.items():
        num_seg = len(model.time_season[p]) * len(model.time_of_day)
        if count > 0:
            model.is_capacity_factor_process[r, p, t, v] = True
            if count < num_seg:
                logger.info(
                    'Some but not all processes were set in capacity_factor_process (%i out of a '
                    'possible %i) for: %s Missing values will default to capacity_factor_tech '
                    'value or 1 if that is not set either.',
                    count,
                    num_seg,
                    (r, p, t, v),
                )


@deprecated('should not be needed.  We are pulling the default on-the-fly where used')
def create_capacity_factors(model: TemoaModel) -> None:
    """
    Steps to creating capacity factors:
    1. Collect all possible processes
    2. Find the ones _not_ specified in capacity_factor_process
    3. Set them, based on capacity_factor_tech.
    """
    capacity_factor_process = model.capacity_factor_process

    # Step 1
    processes = {(r, t, v) for r, i, t, v, o in model.efficiency.sparse_iterkeys()}

    all_cfs = {
        (r, p, s, d, t, v)
        for (r, t, v) in processes
        for p in model.process_periods[r, t, v]
        for s, d in cross_product(model.time_season[p], model.time_of_day)
    }

    # Step 2
    unspecified_cfs = all_cfs.difference(capacity_factor_process.sparse_iterkeys())

    # Step 3

    # Some hackery: We futz with _constructed because Pyomo thinks that this
    # Param is already constructed.  However, in our view, it is not yet,
    # because we're specifically targeting values that have not yet been
    # constructed, that we know are valid, and that we will need.

    if unspecified_cfs:
        # CFP._constructed = False
        for r, p, s, d, t, v in unspecified_cfs:
            capacity_factor_process[r, p, s, d, t, v] = model.capacity_factor_tech[r, p, s, d, t]
        logger.debug(
            'Created Capacity Factors for %d processes without an explicit specification',
            len(unspecified_cfs),
        )
    # CFP._constructed = True


def get_default_capacity_factor(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> float:
    """
    This initializer is used to fill the capacity_factor_process from the capacity_factor_tech
    where needed.

    Priority:
        1.  As specified in data input (this function not called)
        2.  Here
        3.  The default from capacity_factor_tech param
    :param M: generic model reference
    :param r: region
    :param s: season
    :param d: time-of-day slice
    :param t: tech
    :param v: vintage
    :return: the capacity factor
    """
    return value(model.capacity_factor_tech[r, p, s, d, t])


def get_capacity_factor(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> float:
    if model.is_capacity_factor_process[r, p, t, v]:
        return value(model.capacity_factor_process[r, p, s, d, t, v])
    else:
        return value(model.capacity_factor_tech[r, p, s, d, t])


# ============================================================================
# PYOMO INDEX SETS
# ============================================================================


def capacity_variable_indices(
    model: TemoaModel,
) -> set[tuple[Region, Technology, Vintage]] | None:
    return model.new_capacity_rtv


def retired_capacity_variable_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage]]:
    return {
        (r, p, t, v)
        for r, p, t in model.process_vintages
        if t in model.tech_retirement and t not in model.tech_uncap
        for v in model.process_vintages[r, p, t]
        if v < p <= v + value(model.lifetime_process[r, t, v]) - value(model.period_length[p])
    }


def annual_retirement_variable_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage]]:
    return {
        (r, p, t, v)
        for r, t, v in model.retirement_periods
        for p in model.retirement_periods[r, t, v]
    }


def capacity_available_variable_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology]] | None:
    return model.active_capacity_available_rpt


def regional_exchange_capacity_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Region, Period, Technology, Vintage]]:
    indices: set[tuple[Region, Region, Period, Technology, Vintage]] = set()
    for r_e, p, i in model.export_regions:
        for r_i, t, v, _o in model.export_regions[r_e, p, i]:
            indices.add((r_e, r_i, p, t, v))

    return indices


def capacity_annual_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage]]:
    capacity_indices: set[tuple[Region, Period, Technology, Vintage]] = set()
    if model.active_activity_rptv:
        for r, p, t, v in model.active_activity_rptv:
            if t in model.tech_annual and t not in model.tech_demand:
                if t not in model.tech_uncap:
                    capacity_indices.add((r, p, t, v))
    else:
        return set()

    return capacity_indices


def capacity_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    capacity_indices: set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]] = set()
    if model.active_activity_rptv:
        for r, p, t, v in model.active_activity_rptv:
            if t not in model.tech_annual or t in model.tech_demand:
                if t not in model.tech_uncap:
                    if t not in model.tech_storage:
                        for s in model.time_season[p]:
                            for d in model.time_of_day:
                                capacity_indices.add((r, p, s, d, t, v))
    else:
        return set()

    return capacity_indices


@deprecated('switched over to validator... this set is typically VERY empty')
def capacity_factor_process_indices(
    model: TemoaModel,
) -> set[tuple[Region, Season, TimeOfDay, Technology, Vintage]]:
    indices: set[tuple[Region, Season, TimeOfDay, Technology, Vintage]] = set()
    for r, _i, t, v, _o in model.efficiency.sparse_iterkeys():
        for p in model.time_optimize:
            for s in model.time_season[p]:
                for d in model.time_of_day:
                    indices.add((r, s, d, t, v))
    return indices


def capacity_factor_tech_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology]]:
    all_cfs: set[tuple[Region, Period, Season, TimeOfDay, Technology]] = set()
    if model.active_capacity_available_rpt:
        for r, p, t in model.active_capacity_available_rpt:
            for s in model.time_season[p]:
                for d in model.time_of_day:
                    all_cfs.add((r, p, s, d, t))
    else:
        return set()
    return all_cfs


def capacity_available_variable_indices_vintage(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage]] | None:
    return model.active_capacity_available_rptv


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def annual_retirement_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    Get the annualised retirement rate for a process in a given period.
    Used to output retirement (including end of life, EOL) and to model end of
    life flows and emissions. Assumes that retirement from the beginning of each period
    is evenly distributed over that model period :math:`\frac{1}{\text{LEN}_p}`
    for the accounting of retirement flows (in the same way we assume capacity is
    deployed evenly over the model period for construction inputs and embodied emissions).
    The factor :math:`\frac{\text{LSC}_{r,p,t,v}}{\text{PLF}_{r,p,t,v}}`
    adjusts the average survival during a period to the survival at the beginning
    of that period.

    .. math::
        :label: Annual Retirement

            \textbf{ART}_{r,p,t,v} =
            \begin{cases}
                \frac{1}{\text{LEN}_p} \cdot
                \frac{\text{LSC}_{r,p,t,v}}{\text{PLF}_{r,p,t,v}} \cdot \textbf{CAP}_{r,p,t,v}
                & \text{if EOL} \\
                \frac{1}{\text{LEN}_p} \cdot
                \left(
                \frac{\text{LSC}_{r,p,t,v}}{\text{PLF}_{r,p,t,v}} \cdot \textbf{CAP}_{r,p,t,v}
                - \frac{\text{LSC}_{r,p_{next},t,v}}{\text{PLF}_{r,p_{next},t,v}} \cdot
                \textbf{CAP}_{r,p_{next},t,v}
                \right)
                & \text{otherwise} \\
            \end{cases}

            \\\text{where EOL when } p \leq v + LTP_{r,t,v} < p + LEN_p
    """

    ## Get the capacity at the start of this period
    if p == v + value(model.lifetime_process[r, t, v]):
        # Exact EOL. No v_capacity or v_retired_capacity for this period.
        if p == model.time_optimize.first():
            # Must be existing capacity. Apply survival curve to existing cap
            cap_begin = model.existing_capacity[r, t, v] * model.lifetime_survival_curve[r, p, t, v]
        else:
            # Get previous capacity and continue survival curve
            p_prev = model.time_optimize.prev(p)
            cap_begin = (
                model.v_capacity[r, p_prev, t, v]
                * value(model.lifetime_survival_curve[r, p, t, v])
                / value(model.process_life_frac[r, p_prev, t, v])
            )
    else:
        # The capacity at the beginning of the period
        cap_begin = (
            model.v_capacity[r, p, t, v]
            * value(model.lifetime_survival_curve[r, p, t, v])
            / value(model.process_life_frac[r, p, t, v])
        )

    ## Get the capacity at the end of this period
    if p <= v + value(model.lifetime_process[r, t, v]) < p + value(model.period_length[p]):
        # EOL so capacity ends on zero
        cap_end = 0
    else:
        # Mid-life period, ending capacity is beginning capacity of next period
        p_next = model.time_future.next(p)

        if p == model.time_optimize.last() or p_next == v + value(model.lifetime_process[r, t, v]):
            # No v_capacity or v_retired_capacity for next period so just continue down the
            # survival curve
            cap_end = (
                cap_begin
                * value(model.lifetime_survival_curve[r, p_next, t, v])
                / value(model.lifetime_survival_curve[r, p, t, v])
            )
        else:
            # Get the next period's beginning capacity
            cap_end = (
                model.v_capacity[r, p_next, t, v]
                * value(model.lifetime_survival_curve[r, p_next, t, v])
                / value(model.process_life_frac[r, p_next, t, v])
            )

    annualised_retirement = (cap_begin - cap_end) / model.period_length[p]
    return model.v_annual_retirement[r, p, t, v] == annualised_retirement


def capacity_available_by_period_and_tech_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    r"""

    The :math:`\textbf{CAPAVL}` variable is nominally for reporting solution values,
    but is also used in the Limit constraint calculations.

    .. math::
        :label: CapacityAvailable

        \textbf{CAPAVL}_{r, p, t} = \sum_{v, p_i \leq p} \textbf{CAP}_{r, p, t, v}

        \\
        \forall p \in \text{P}^o, r \in R, t \in T
    """
    cap_avail = sum(model.v_capacity[r, p, t, S_v] for S_v in model.process_vintages[r, p, t])

    expr = model.v_capacity_available_by_period_and_tech[r, p, t] == cap_avail
    return expr


def capacity_annual_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    Similar to Capacity_constraint, but for technologies belonging to the
    :code:`tech_annual`  set. Technologies in the tech_annual set have constant output
    across different timeslices within a year, so we do not need to ensure
    that installed capacity is sufficient across all timeslices, thus saving
    some computational effort. Instead, annual output is sufficient to calculate
    capacity. Hourly capacity factors cannot be defined to annual technologies
    but annual capacity factors can be set using limit_annual_capacity_factor,
    which will be implicitly accounted for here.

    .. math::
        :label: CapacityAnnual

            \text{C2A}_{r, t}
            \cdot \textbf{CAP}_{r, t, v}
        =
            \sum_{I, O} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

        \\
        \forall \{r, p, t \in T^{a}, v\} \in \Theta_{\text{Activity}}
    """
    activity_rptv = sum(
        model.v_flow_out_annual[r, p, S_i, t, v, S_o]
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    return value(model.capacity_to_activity[r, t]) * model.v_capacity[r, p, t, v] >= activity_rptv


def capacity_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    This constraint ensures that the capacity of a given process is sufficient
    to support its activity across all time periods and time slices. The calculation
    on the left hand side of the equality is the maximum amount of energy a process
    can produce in the timeslice :code:`(s,d)`. Note that the curtailment variable
    shown below only applies to technologies that are members of the curtailment set.
    Curtailment is necessary to track explicitly in scenarios that include a high
    renewable target. Without it, the model can generate more activity than is used
    to meet demand, and have all activity (including the portion curtailed) count
    towards the target. Tracking activity and curtailment separately prevents this
    possibility.

    .. math::
       :label: Capacity

           \left (
                   \text{CFP}_{r, p, s, d, t, v}
             \cdot \text{C2A}_{r, t}
             \cdot \text{SEG}_{s, d}
           \right )
           \cdot \textbf{CAP}_{r, t, v}
           =
           \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}
           +
           \sum_{I, O} \textbf{CUR}_{r, p, s, d, i, t, v, o}

       \\
       \forall \{r, p, s, d, t, v\} \in \Theta_{\text{FO}}
    """
    # The expressions below are defined in-line to minimize the amount of
    # expression cloning taking place with Pyomo.

    if t in model.tech_annual:
        # Annual demand technology
        useful_activity = sum(
            (
                value(model.demand_specific_distribution[r, p, s, d, S_o])
                if S_o in model.commodity_demand
                else value(model.segment_fraction[p, s, d])
            )
            * model.v_flow_out_annual[r, p, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
    else:
        useful_activity = sum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )

    if t in model.tech_curtailment:
        # If technologies are present in the curtailment set, then enough
        # capacity must be available to cover both activity and curtailment.
        return get_capacity_factor(model, r, p, s, d, t, v) * value(
            model.capacity_to_activity[r, t]
        ) * value(model.segment_fraction[p, s, d]) * model.v_capacity[
            r, p, t, v
        ] == useful_activity + sum(
            model.v_curtailment[r, p, s, d, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
    else:
        return (
            get_capacity_factor(model, r, p, s, d, t, v)
            * value(model.capacity_to_activity[r, t])
            * value(model.segment_fraction[p, s, d])
            * model.v_capacity[r, p, t, v]
            >= useful_activity
        )


def adjusted_capacity_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    This constraint updates the capacity of a process by taking into account retirements
    and end of life. For a given :code:`(r,p,t,v)` index, this constraint sets the capacity
    equal to the amount installed in period :code:`v` and subtracts from it any and all retirements
    that occurred prior to the period in question, :code:`p`, and end of life from the
    survival curve if defined. It finally adjusts for the process life fraction, which
    accounts for a possible mid-period end of life where, for example, EOL 3 years into a 5-year
    period would be treated as :math:`\frac{3}{5}` capacity for all 5 years.

    .. figure:: images/adjusted_capacity_plf.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 50%

        For processes reaching end of life mid-period, the process life fraction adjustment is
        applied, distributing the effective capacity over the whole period.

    For processes using survival curves, the yearly survival curve :math:`\text{LSC}_{r,p,t,v}` is
    averaged over the period to get the effective remaining capacity for that period  Because this
    implicitly handles mid-period end of life, :math:`\text{PLF}_{r,p,t,v}` is used to account for
    both phenomena.

    .. figure:: images/adjusted_capacity_sc.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 50%

        For processes with a defined survival curve, the surviving capacity is averaged over each
        period to get the adjusted capacity. This implicitly handles mid-period end of life as a
        survival curve will always be zero after the end of life of a process.

    .. math::
        :label: Adjusted Capacity

            \textbf{CAP}_{r,p,t,v} =
            \begin{cases}
                \text{PLF}_{r,p,t,v} \cdot
                \left(
                \text{ECAP}_{r,t,v} - \sum\limits_{v < p' <= p}
                \frac{\textbf{RCAP}_{r,p',t,v}}{\text{LSC}_{r,p',t,v}}
                \right)
                & \text{if } \ v \in T^e \\
                \text{PLF}_{r,p,t,v} \cdot
                \left(
                \textbf{NCAP}_{r,t,v} - \sum\limits_{v < p' <= p}
                \frac{\textbf{RCAP}_{r,p',t,v}}{\text{LSC}_{r,p',t,v}}
                \right)
                & \text{if } \ v \notin T^e
            \end{cases}

            \\\text{where }
            \text{PLF}_{r,p,t,v} =
            \begin{cases}
                \frac{1}{\text{LEN}_p} \cdot \left(
                \sum\limits_{y = p}^{p+\text{LEN}_{p}-1}{\text{LSC}_{r,y,t,v}}
                \right)
                & \text{if } t \in T^{sc} \\
                \frac{1}{\text{LEN}_p} \cdot \left( v + \text{LTP}_{r,t,v} - p \right)
                & \text{if } t \notin T^{sc} \\
            \end{cases}

    We divide :math:`\frac{\textbf{RCAP}_{r,p',t,v}}{\text{LSC}_{r,p',t,v}}`
    because the average survival factor in :math:`\text{PLF}_{r,p,t,v}` is indexed to the vintage
    period (the beginning of the survival curve). So, we adjust for the relative survival from
    the time when that retirement occurred (treated here as at the beginning of each period).
    """

    if v in model.time_exist:
        built_capacity = value(model.existing_capacity[r, t, v])
    else:
        built_capacity = model.v_new_capacity[r, t, v]

    early_retirements = 0
    if t in model.tech_retirement:
        early_retirements = sum(
            model.v_retired_capacity[r, S_p, t, v]
            / value(model.lifetime_survival_curve[r, S_p, t, v])
            for S_p in model.time_optimize
            if v < S_p <= p
            and S_p < v + value(model.lifetime_process[r, t, v]) - value(model.period_length[S_p])
        )

    remaining_capacity = (built_capacity - early_retirements) * value(
        model.process_life_frac[r, p, t, v]
    )
    return model.v_capacity[r, p, t, v] == remaining_capacity


# ============================================================================
# PRE-COMPUTATION FUNCTIONS
# ============================================================================


def create_capacity_and_retirement_sets(model: TemoaModel) -> None:
    """
    Creates and populates component-specific Python sets and dictionaries on the model object.

    This function is called once during model initialization and is responsible for
    creating the sparse indices related to technology capacity, retirement, and
    construction/end-of-life material flows. These data structures are then
    used by other functions in this module to build Pyomo components.

    Populates:
        - model.retirement_periods: dict mapping (r, t, v) to a set of periods `p`
          where retirement can occur.
        - model.capacity_consumption_techs: dict mapping (r, v, i) to a set of techs `t`
          that consume commodity `i` for construction.
        - model.retirement_production_processes: dict mapping (r, p, o) to a set of `(t, v)`
          processes that produce commodity `o` at end-of-life.
        - model.new_capacity_rtv: set of (r, t, v) for new capacity investments.
        - model.active_capacity_available_rpt: set of (r, p, t) where capacity is active.
        - model.active_capacity_available_rptv: set of (r, p, t, v) where vintage capacity is
          active.
    """

    logger.debug('Creating capacity, retirement, and construction/EOL sets.')
    # Calculate retirement periods based on lifetime and survival curves
    for r, _i, t, v, _o in model.efficiency.sparse_iterkeys():
        lifetime = value(model.lifetime_process[r, t, v])
        for p in model.time_optimize:
            is_natural_eol = p <= v + lifetime < p + value(model.period_length[p])
            is_early_retire = t in model.tech_retirement and v < p <= v + lifetime - value(
                model.period_length[p]
            )
            is_survival_curve = model.is_survival_curve_process[r, t, v] and v <= p <= v + lifetime

            if t not in model.tech_uncap and any(
                (is_natural_eol, is_early_retire, is_survival_curve)
            ):
                model.retirement_periods.setdefault((r, t, v), set()).add(p)

    # Link construction materials to technologies
    for r, i, t, v in model.construction_input.sparse_iterkeys():
        model.capacity_consumption_techs.setdefault((r, v, i), set()).add(t)

    # Link end-of-life materials to retiring technologies
    for r, t, v, o in model.end_of_life_output.sparse_iterkeys():
        if (r, t, v) in model.retirement_periods:
            for p in model.retirement_periods[r, t, v]:
                model.retirement_production_processes.setdefault((r, p, o), set()).add((t, v))

    # Create active capacity index sets from the now-populated process_vintages
    model.new_capacity_rtv = {
        (r, t, v)
        for r, p, t in model.process_vintages
        for v in model.process_vintages[r, p, t]
        if t not in model.tech_uncap and v in model.time_optimize
    }
    model.active_capacity_available_rpt = {
        (r, p, t)
        for r, p, t in model.process_vintages
        if model.process_vintages[r, p, t] and t not in model.tech_uncap
    }
    model.active_capacity_available_rptv = {
        (r, p, t, v)
        for r, p, t in model.process_vintages
        for v in model.process_vintages[r, p, t]
        if t not in model.tech_uncap
    }
