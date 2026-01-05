# temoa/components/storage.py
"""
Defines the energy storage-related components of the Temoa model.

This module is responsible for modeling the behavior of storage technologies,
including:
-  Defining the state variables for storage levels (both daily and seasonal).
-  Enforcing the conservation of energy from one time slice to the next.
-  Constraining the storage level to be within the device's energy capacity.
-  Constraining the charge, discharge, and throughput rates to be within the
    device's power capacity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyomo.environ import Constraint, value

from .utils import Operator, get_variable_efficiency, operator_expression

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

    from ..types import ExprLike, Period, Region, Season, Technology, TimeOfDay, Vintage


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def storage_level_variable_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]] | None:
    return model.storage_level_indices_rpsdtv


def seasonal_storage_level_variable_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, Technology, Vintage]] | None:
    return model.seasonal_storage_level_indices_rpstv


def seasonal_storage_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    if model.seasonal_storage_level_indices_rpstv:
        indices = {
            (r, p, s, d, t, v)
            for r, p, s, t, v in model.seasonal_storage_level_indices_rpstv
            for d in model.time_of_day
        }
        return indices
    return set()


def storage_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]] | None:
    return model.storage_level_indices_rpsdtv


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================

# --- Core Energy Balance Constraints ---


def storage_energy_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    This constraint enforces the continuity of storage level between time slices.
    storage level in the next time slice (:math:`s_{next}, d_{next}`) is equal to
    current storage level plus net charge in the current time slice.

    .. math::
        :label: Storage Energy

            {SL}_{r,p,s,d,t,v}
            + \sum\limits_{I,O} \mathbf{FIS}_{r,p,s,d,i,t,v,o} \cdot {EFF}_{r,i,t,v,o}
            - \sum\limits_{I,O} \mathbf{FO}_{r,p,s,d,i,t,v,o}
            = {SL}_{r,p,s_{{next}},d_{{next}},t,v}

    Note that for all seasonal representations except consecutive_days, the last time slice
    of each season will loop back to the first time slice of the same season, preventing
    seasonal deltas for non-seasonal storage (see SeasonalStorageEnergyUpperBound).
    """

    # We allow a non-zero daily delta only in the case of seasonal storage
    if model.is_seasonal_storage[t] and d == model.time_of_day.last():
        return Constraint.Skip  # handled by SeasonalStorageEnergy_constraint

    # This is the sum of all input=i sent TO storage tech t of vintage v with
    # output=o in p,s,d
    charge = sum(
        model.v_flow_in[r, p, s, d, S_i, t, v, S_o]
        * get_variable_efficiency(model, r, p, s, d, S_i, t, v, S_o)
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    # This is the sum of all output=o withdrawn FROM storage tech t of vintage v
    # with input=i in p,s,d
    discharge = sum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for S_o in model.process_outputs[r, p, t, v]
        for S_i in model.process_inputs_by_output[r, p, t, v, S_o]
    )

    stored_energy = charge - discharge

    s_next: Season
    d_next: TimeOfDay
    s_next, d_next = model.time_next[p, s, d]

    expr = (
        model.v_storage_level[r, p, s, d, t, v] + stored_energy
        == model.v_storage_level[r, p, s_next, d_next, t, v]
    )

    return expr


def seasonal_storage_energy_constraint(
    model: TemoaModel, r: Region, p: Period, s_seq: Season, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    This constraint enforces the continuity of state of charge between seasons for seasonal
    storage. Sequential season storage level increases by the matched season's net charge
    over that entire day, adjusted for number of days represented by sequential vs non-sequential
    seasons. Only applies to storage technologies in the :code:`tech_seasonal_storage` set.
    :math:`s^*` represents the matching non-sequential season for the sequential season
    :math:`s^{seq}`.

    .. math::
        :label: Storage Energy (Sequential Seasons)

        \mathbf{SSL}_{r,p,s^{seq},t,v}
        + DA_{r,p,s^{seq}} \cdot \left(\mathbf{SL}_{r,p,s^*,d_{last},t,v} +
        \sum_{I,O} \mathbf{FI}_{r,p,s^*,d_{last},i,t,v,o} \cdot EFF_{r,i,t,v,o}
        - \sum_{I,O} \mathbf{FO}_{r,p,s^*,d_{last},i,t,v,o}
        \right)

        = DA_{r,p,s^{seq}_{next}} \cdot \mathbf{SL}_{r,p,s_{next}^*,d_{first},t,v}
        + \mathbf{SSL}_{r,p,s^{seq}_{next},t,v}

        \\
        \text{where } DA_{r,p,s^{seq}} = \frac{\#days_{s^{seq}}}{SEG_{r,p,s^*} \cdot DPP}

    .. figure:: images/ldes_chain.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 60%

        How sequential seasons chain together for seasonal storage. Hatched area is
        seasonal_storage_level :math:`SSL_{r,p,s^{seq},t,v}`. Vertical lines are
        StorageLevel :math:`SL_{r,p,s^*,d,t,v}`. Green line is net seasonal storage
        level :math:`SSL_{r,p,s^{seq},t,v} + SL_{r,p,s^*,d,t,v}`. Background grey
        lines show how storage levels from non-sequential seasons are combined
        in sequential seasons. Dashed line is SeasonalStorageEnergyUpperBound.
        Sequential seasons two and four here are each two days while one and three
        are each one day.
    """

    s: Season = model.sequential_to_season[p, s_seq]

    # This is the sum of all input=i sent TO storage tech t of vintage v with
    # output=o in p,s
    charge = sum(
        model.v_flow_in[r, p, s, model.time_of_day.last(), S_i, t, v, S_o]
        * get_variable_efficiency(model, r, p, s, model.time_of_day.last(), S_i, t, v, S_o)
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    # This is the sum of all output=o withdrawn FROM storage tech t of vintage v
    # with input=i in p,s
    discharge = sum(
        model.v_flow_out[r, p, s, model.time_of_day.last(), S_i, t, v, S_o]
        for S_o in model.process_outputs[r, p, t, v]
        for S_i in model.process_inputs_by_output[r, p, t, v, S_o]
    )

    s_seq_next: Season = model.time_next_sequential[p, s_seq]
    s_next: Season = model.sequential_to_season[p, s_seq_next]

    # Flows and StorageLevel are normalised to the number of days in the non-sequential season,
    # so must
    # be adjusted to the number of days in the sequential season
    days_adjust = value(model.time_season_sequential[p, s_seq, s]) / (
        value(model.segment_fraction_per_season[p, s]) * value(model.days_per_period)
    )
    days_adjust_next = value(model.time_season_sequential[p, s_seq_next, s_next]) / (
        value(model.segment_fraction_per_season[p, s_next]) * value(model.days_per_period)
    )

    stored_energy = (charge - discharge) * days_adjust

    start = (
        model.v_seasonal_storage_level[r, p, s_seq, t, v]
        + model.v_storage_level[r, p, s, model.time_of_day.last(), t, v] * days_adjust
    )
    end = (
        model.v_seasonal_storage_level[r, p, s_seq_next, t, v]
        + model.v_storage_level[r, p, s_next, model.time_of_day.first(), t, v] * days_adjust_next
    )

    expr = start + stored_energy == end
    return expr


# --- Capacity and Rate Limit Constraints ---


def storage_energy_upper_bound_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    This constraint ensures that the amount of energy stored does not exceed
    the upper bound set by the energy capacity of the storage device, as calculated
    on the right-hand side.

    Because the number and duration of time slices are user-defined, we need to adjust
    the storage duration, which is specified in hours. First, the hourly duration is divided
    by the number of hours in a year to obtain the duration as a fraction of the year.
    Since the :math:`C2A` parameter assumes the conversion of capacity to annual activity,
    we need to express the storage duration as fraction of a year. Then, :math:`SEG_{s,d}`
    summed over the time-of-day slices (:math:`d`) multiplied by :math:`DPP` yields the
    number of days per season. This step is necessary because conventional time sliced models
    use a single day to represent many days within a given season. Thus, it is necessary to
    scale the storage duration to account for the number of days in each season.

    .. math::
       :label: StorageEnergyUpperBound

          \textbf{SL}_{r, p, s, d, t, v} \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot \frac {SD_{r,t}}{24 \cdot DPP}
          \cdot \sum_{d} SEG_{s,d} \cdot DPP

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageEnergyUpperBound}}

    A season can represent many days. Within each season, flows are multiplied by the
    number of days each season represents and, so, the upper bound needs to be adjusted
    to allow day-scale flows (e.g., charge in the morning, discharge in the afternoon).

    .. figure:: images/daily_storage_representation.*
        :align: center
        :width: 100%
        :figclass: center
        :figwidth: 40%

        Representation of a 3-day season for non-seasonal (daily) storage.
    """

    if model.is_seasonal_storage[t]:
        return Constraint.Skip  # redundant on SeasonalStorageEnergyUpperBound

    energy_capacity = (
        model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * (value(model.storage_duration[r, t]) / (24 * value(model.days_per_period)))
        * value(model.segment_fraction_per_season[p, s])
        * model.days_per_period  # adjust for days in season
    )

    expr = model.v_storage_level[r, p, s, d, t, v] <= energy_capacity

    return expr


def seasonal_storage_energy_upper_bound_constraint(
    model: TemoaModel, r: Region, p: Period, s_seq: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    Builds off of StorageEnergyUpperBound_constraint. Enforces the max charge capacity
    of seasonal storage, summing the real storage level with the superimposed sequential
    seasonal storage level. :math:`s^*` represents the matching non-sequential season for
    the sequential season :math:`s^{seq}`.

    .. math::
        :label: Seasonal Storage Energy Capacity

        \mathbf{SSL}_{r,p,s^{seq},t,v}
        + \mathbf{SL}_{r,p,s^*,d,t,v} \cdot DA_{r,p,s^{seq}}
        \leq \mathbf{CAP}_{r,p,t,v} \cdot C2A_{r,t} \cdot \frac{SD_{r,t}}{24 \cdot DPP}

        \\

        \text{where } DA_{r,p,s^{seq}} = \frac{\#days_{s^{seq}}}{SEG_{r,p,s^*} \cdot DPP}



    Unlike non-seasonal (daily) storage, seasonal storage is allowed to carry energy
    between seasons. However, through seasons representing multiple days, many days'
    charge deltas have accumulated, multiplied by the number of days the season
    represents. If we allowed these stacked deltas to carry between seasons then we would
    be multiplying the effective energy capacity of the storage. We could just constrain
    the seasonal delta to the unadjusted energy capacity, but then the final day in the
    season would sit atop a season's worth of deltas, possibly exceeding our upper or
    lower bound by a factor of :math:`\frac{N-1}{N}` where :math:`N` is the number of
    days the sequential season represents.

    .. figure:: images/ldes_delta_problem.*
        :align: center
        :width: 100%
        :figclass: center
        :figwidth: 100%

        The energy upper bound or non-negative lower bound could be violated in a
        season representing multiple days if we both adjusted the upper bound to
        the number of days and allowed a seasonal delta.

    So, we do not adjust the upper energy bound for seasonal storage. This limits the
    ability of seasonal storage to perform arbitrage within each season, but allows it to
    carry energy between seasons realistically.

    .. figure:: images/ldes_delta_representation.*
        :align: center
        :width: 100%
        :figclass: center
        :figwidth: 40%

        Unadjusted energy upper bound constraint for seasonal storage.
    """

    s: Season = model.sequential_to_season[p, s_seq]

    energy_capacity = (
        model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * (value(model.storage_duration[r, t]) / (24 * value(model.days_per_period)))
    )

    # Flows and StorageLevel are normalised to the number of days in the non-sequential season,
    # so must
    # be adjusted to the number of days in the sequential season
    days_adjust = value(model.time_season_sequential[p, s_seq, s]) / (
        value(model.segment_fraction_per_season[p, s]) * value(model.days_per_period)
    )

    # v_storage_level tracks the running cumulative delta in the non-sequential season,
    # so must be adjusted
    # to the size of the sequential season
    running_day_delta = model.v_storage_level[r, p, s, d, t, v] * days_adjust

    expr = model.v_seasonal_storage_level[r, p, s_seq, t, v] + running_day_delta <= energy_capacity

    return expr


def storage_charge_rate_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""

    This constraint ensures that the charge rate of the storage unit is
    limited by the power capacity (typically GW) of the storage unit.

    .. math::
       :label: StorageChargeRate

          \sum_{I, O} \textbf{FIS}_{r, p, s, d, i, t, v, o} \cdot EFF_{r,i,t,v,o}
          \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot SEG_{s,d}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageChargeRate}}

    """
    # Calculate energy charge in each time slice
    slice_charge = sum(
        model.v_flow_in[r, p, s, d, S_i, t, v, S_o]
        * get_variable_efficiency(model, r, p, s, d, S_i, t, v, S_o)
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    # Maximum energy charge in each time slice
    max_charge = (
        model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * value(model.segment_fraction[p, s, d])
    )

    # Energy charge cannot exceed the power capacity of the storage unit
    expr = slice_charge <= max_charge

    return expr


def storage_discharge_rate_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""

    This constraint ensures that the discharge rate of the storage unit
    is limited by the power capacity (typically GW) of the storage unit.

    .. math::
       :label: StorageDischargeRate

          \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}
          \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot SEG_{s,d}

          \\
          \forall \{r,p, s, d, t, v\} \in \Theta_{\text{StorageDischargeRate}}
    """
    # Calculate energy discharge in each time slice
    slice_discharge = sum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for S_o in model.process_outputs[r, p, t, v]
        for S_i in model.process_inputs_by_output[r, p, t, v, S_o]
    )

    # Maximum energy discharge in each time slice
    max_discharge = (
        model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * value(model.segment_fraction[p, s, d])
    )

    # Energy discharge cannot exceed the capacity of the storage unit
    expr = slice_discharge <= max_discharge

    return expr


def storage_throughput_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> ExprLike:
    r"""

    It is not enough to only limit the charge and discharge rate separately. We also
    need to ensure that the maximum throughput (charge + discharge) does not exceed
    the capacity (typically GW) of the storage unit.

    .. math::
       :label: StorageThroughput

          \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}
          +
          \sum_{I, O} \textbf{FIS}_{r, p, s, d, i, t, v, o} \cdot EFF_{r,i,t,v,o}
          \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot SEG_{s,d}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageThroughput}}
    """
    discharge = sum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for S_o in model.process_outputs[r, p, t, v]
        for S_i in model.process_inputs_by_output[r, p, t, v, S_o]
    )

    charge = sum(
        model.v_flow_in[r, p, s, d, S_i, t, v, S_o]
        * get_variable_efficiency(model, r, p, s, d, S_i, t, v, S_o)
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    throughput = charge + discharge
    max_throughput = (
        model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * value(model.segment_fraction[p, s, d])
    )
    expr = throughput <= max_throughput
    return expr


# A limit but more cohesive here than in limits.py
def limit_storage_fraction_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
    op: str,
) -> ExprLike:
    r"""

    This constraint is used if the users wishes to force a specific storage charge level
    for certain storage technologies and vintages at a certain time slice.
    In this case, the value of the decision variable :math:`\textbf{SI}_{r,t,v}` is set by
    this constraint rather than being optimized. User-specified storage charge levels that are
    sufficiently different from the optimal :math:`\textbf{SI}_{r,t,v}` could impact the
    cost-effectiveness of storage. For example, if the optimal charge level happens to be
    50% of the full energy capacity, forced charge levels (specified by parameter
    :math:`SIF_{r,t,v}`) equal to 10% or 90% of the full energycapacity could lead to
    more expensive solutions.


    .. math::
       :label: limit_storage_fraction

          \textbf{SF}_{r,p,s,d,t,v} \le
          SF_{r,p,s,d,t,v}
          \cdot
          \textbf{CAP}_{r,p,t,v} \cdot \text{C2A}_{r,t} \cdot \frac {SD_{r,t}}{24 \cdot \text{DPP}}
          \cdot \sum_{d} \text{SEG}_{s,d} \cdot \text{days\_per\_period} \cdot \text{MPL}_{r,p,t,v}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{limit\_storage\_fraction}}
    """

    energy_limit = (
        model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * (value(model.storage_duration[r, t]) / (24 * value(model.days_per_period)))
        * value(model.limit_storage_fraction[r, p, s, d, t, v, op])
    )

    if model.is_seasonal_storage[t]:
        s_seq: Season = s  # sequential season
        s = model.sequential_to_season[p, s_seq]  # non-sequential season

    # adjust the storage level to the individual-day level
    energy_level = model.v_storage_level[r, p, s, d, t, v] / (
        value(model.segment_fraction_per_season[p, s]) * value(model.days_per_period)
    )

    if model.is_seasonal_storage[t]:
        # seasonal storage upper energy limit is absolute
        energy_level = model.v_seasonal_storage_level[r, p, s_seq, t, v] + energy_level * value(
            model.time_season_sequential[p, s_seq, s]
        )

    expr = operator_expression(energy_level, Operator(op), energy_limit)

    return expr
