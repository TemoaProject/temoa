from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pyomo.environ import quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology
from temoa.components import capacity
from temoa.components.costs import loan_cost, loan_cost_survival_curve

if TYPE_CHECKING:
    from pyomo.core import Expression
    from pyomo.core.base.objective import ObjectiveData
    from pyomo.core.base.var import VarData

    from temoa.extensions.economies_of_scale.core.model import EOSModel
    from temoa.types import ExprLike, Period, Region, Technology

logger = logging.getLogger(__name__)


# --- Initialise EOS invest model components ---
def cost_invest_eos_cumulative_capacity_indices(
    model: EOSModel,
) -> set[tuple[Region, Period, Technology, int]]:
    return {
        (r, _p, t, n)
        for r, t, n in model.cost_invest_eos.sparse_keys()
        for _p in model.time_optimize
        for _r, _t in capacity.gather_group_built_processes(model, r, t, _p)
    }


def cost_invest_eos_period_cost_indices(model: EOSModel) -> set[tuple[Region, Period, Technology]]:
    return {(r, p, t) for r, p, t, _ in model.cost_invest_eos_segment_rptn}


def append_cost_invest_eos_rtv(model: EOSModel) -> None:
    """
    EOS invest processes most likely do not have a cost_invest parameter, as
    that is handled by the EOS cost curve.  As a result they would not have
    loan parameters either.  We add these rtv indices to the base
    cost_invest param so EOS invest processes have loan parameters for
    discounting in the objective function.
    """
    for r, p, t in model.cost_invest_eos_period_rpt:
        valid_rtv = {
            (_r, _t, p) for _r, _t in capacity.gather_group_built_processes(model, r, t, p)
        }
        for rtv in valid_rtv:
            if rtv not in model.cost_invest_rtv:
                model.cost_invest_rtv.add(rtv)


def initialize_cost_invest_eos(model: EOSModel) -> None:
    """
    Gather segment data and validate guard rails for EOS invest clusters.
    """

    # Collect segment indices n for each (r,t) cluster; order doesn't matter
    for r, t, n in model.cost_invest_eos.sparse_keys():
        model.cost_invest_eos_segments.setdefault((r, t), set()).add(n)

    # Check that costs and capacities are monotonically increasing
    for (r, t), segs in model.cost_invest_eos_segments.items():
        sorted_segs = sorted(segs)
        for i, n in enumerate(sorted_segs):
            cap_lower, cap_upper, cost_lower, cost_upper = model.cost_invest_eos[r, t, n]

            # Check cost curve is nonnegative and monotonically increasing.
            # If someone wants to break this assumption they should have the
            # skills to edit this code.
            if not all(
                (
                    cap_lower >= 0,
                    cap_upper >= 0,
                    cost_lower >= 0,
                    cost_upper >= 0,
                    cap_upper > cap_lower,
                    cost_upper > cost_lower,
                )
            ):
                msg = (
                    'Negative values or non-increasing segment bounds found '
                    f'in cost_invest_eos table for {r, t, n}'
                )
                logger.error(msg)
                raise ValueError(msg)

            # Backcheck for monotonic growth
            if i == 0:
                continue

            _, prev_cap_upper, _, prev_cost_upper = model.cost_invest_eos[r, t, sorted_segs[i - 1]]

            if not all(
                (
                    abs(cap_lower - prev_cap_upper) <= 0.001,
                    abs(cost_lower - prev_cost_upper) <= 0.001,
                )
            ):
                msg = (
                    'Segments in cost_invest_eos table do not align on their bounds. This would '
                    'leave gaps in the cost curve and could lead to infeasibility. Check '
                    f'({r, t, sorted_segs[i - 1]}) to ({r, t, n})'
                )
                logger.error(msg)
                raise ValueError(msg)

    # Shortens some lines below in error checks
    life = model.lifetime_process
    loan_life = model.loan_lifetime_process
    loan_rate = model.loan_rate

    # Get a viable built process for each EOS invest period, for discounting
    # parameters.  Check that all r, t combos in the cluster share the same
    # lifetime and loan parameters.
    for r, p, t in model.cost_invest_eos_period_rpt:
        for _r, _t in capacity.gather_group_built_processes(model, r, t, p):
            # Store first valid process as our reference for this period
            if (r, p, t) not in model.cost_invest_eos_reference_process:
                model.cost_invest_eos_reference_process[r, p, t] = _r, _t

            # Check that the assumptions hold
            r0, t0 = model.cost_invest_eos_reference_process[r, p, t]
            if any(
                (
                    abs(life[r0, t0, p] - life[_r, _t, p]) >= 0.001,
                    abs(loan_life[r0, t0, p] - loan_life[_r, _t, p]) >= 0.001,
                    abs(loan_rate[r0, t0, p] - loan_rate[_r, _t, p]) >= 0.001,
                )
            ):
                msg = (
                    'Processes assigned to the same cost_invest_eos cost curve must all have '
                    'the same process lifetime, loan lifetime, and loan rate. These two '
                    'processes do not match:\n '
                    f'({r0}, {t0}, {p}) : lifetime = {life[r0, t0, p]}, '
                    f'loan life = {loan_life[r0, t0, p]}, loan rate = {loan_rate[r0, t0, p]}\n'
                    f'({_r}, {_t}, {p}) : lifetime = {life[_r, _t, p]}, '
                    f'loan life = {loan_life[_r, _t, p]}, loan rate = {loan_rate[_r, _t, p]}'
                )
                logger.error(msg)
                raise ValueError(msg)


# --- Enforce the rules of cumulative capacity progression up the cost curve ---
def cost_invest_eos_segment_binary_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    r"""
    Enforce exactly one active segment of the EOS invest cost curve for each
    cluster in each period.

    Each technology cluster :math:`(r, t)` has a piecewise-linear investment
    cost curve split into :math:`N_{r,t}` segments.  The binary variable
    :math:`\textbf{CIEB}_{r,p,t,n}` selects which segment is currently active.
    Exactly one segment must be active at all times:

    .. math::
        :label: Cost Invest EOS Segment Binary Constraint

        \sum_{n \in N_{r,t}} \textbf{CIEB}_{r,p,t,n} = 1

        \qquad \forall \{r, p, t\} \in \Theta_{\text{cost\_invest\_eos\_period\_rpt}}

    where :math:`\textbf{CIEB}_{r,p,t,n}` is
    :code:`v_cost_invest_eos_segment_binary[r, p, t, n]` (:math:`\in \{0, 1\}`) and
    :math:`N_{r,t}` is the set of segment indices declared for cluster
    :math:`(r, t)` in the :code:`cost_invest_eos` table.
    """
    count_active_segments = quicksum(
        model.v_cost_invest_eos_segment_binary[r, p, t, n]
        for n in model.cost_invest_eos_segments[r, t]
    )
    return count_active_segments == 1


def cost_invest_eos_capacity_lower_bound_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology, n: int
) -> ExprLike:
    r"""
    Enforce the lower bound of the active EOS invest cost-curve segment on
    cumulative capacity.

    When segment :math:`n` is inactive (:math:`\textbf{CIEB}_{r,p,t,n} = 0`), the
    right-hand side collapses to zero so the constraint is non-binding.  When
    segment :math:`n` is active (:math:`\textbf{CIEB}_{r,p,t,n} = 1`), it
    enforces that cumulative capacity has reached at least the lower boundary
    :math:`\underline{K}_{r,t,n}` of that segment:

    .. math::
        :label: Cost Invest EOS Capacity Lower Bound

        \textbf{CIECAP}_{r,p,t,n}
            \ge \textbf{CIEB}_{r,p,t,n} \cdot \underline{K}_{r,t,n}

        \qquad \forall \{r, p, t, n\} \in \Theta_{\text{cost\_invest\_eos\_segment\_rptn}}

    where :math:`\textbf{CIECAP}_{r,p,t,n}` is
    :code:`v_cost_invest_eos_cumulative_capacity[r, p, t, n]`,
    :math:`\textbf{CIEB}_{r,p,t,n}` is
    :code:`v_cost_invest_eos_segment_binary[r, p, t, n]`, and
    :math:`\underline{K}_{r,t,n}` is :code:`cost_invest_eos[r, t, n][0]`
    (the :code:`capacity_lower` column).
    """
    cap_lower = model.v_cost_invest_eos_segment_binary[r, p, t, n] * value(
        model.cost_invest_eos[r, t, n][0]
    )
    return model.v_cost_invest_eos_cumulative_capacity[r, p, t, n] >= cap_lower


def cost_invest_eos_capacity_upper_bound_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology, n: int
) -> ExprLike:
    r"""
    Enforce the upper bound of the active EOS invest cost-curve segment on
    cumulative capacity.

    This is the mirror of the lower bound.  When segment :math:`n` is inactive
    the right-hand side collapses to zero, driving
    :math:`\textbf{CIECAP}_{r,p,t,n}` to zero.  When it is active,
    cumulative capacity cannot exceed the upper boundary
    :math:`\overline{K}_{r,t,n}` of that segment:

    .. math::
        :label: Cost Invest EOS Capacity Upper Bound

        \textbf{CIECAP}_{r,p,t,n}
            \le \textbf{CIEB}_{r,p,t,n} \cdot \overline{K}_{r,t,n}

        \qquad \forall \{r, p, t, n\} \in \Theta_{\text{cost\_invest\_eos\_segment\_rptn}}

    where :math:`\overline{K}_{r,t,n}` is :code:`cost_invest_eos[r, t, n][1]`
    (the :code:`capacity_upper` column).

    Together the lower and upper bound constraints implement a "big-M"-style
    activation: only the single active segment can carry non-zero capacity,
    and that capacity is pinned within the segment's range.
    """
    cap_upper = model.v_cost_invest_eos_segment_binary[r, p, t, n] * value(
        model.cost_invest_eos[r, t, n][1]
    )
    return model.v_cost_invest_eos_cumulative_capacity[r, p, t, n] <= cap_upper


def cost_invest_eos_cumulative_capacity_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    r"""
    Equate the EOS invest cumulative-capacity expression to the actual capacity
    built in the base model.

    The EOS invest formulation tracks cumulative capacity internally through
    :math:`\textbf{CIECAP}_{r,p,t,n}`.  This constraint ties those internal
    variables to the real decision variables :math:`\textbf{NCAP}_{r,t,v}` and
    the parameter :math:`\textbf{ECAP}_{r,t,v}` from the base Temoa model, so
    the cost curve reflects actually-built capacity rather than a free
    parameter:

    .. math::
        :label: Cost Invest EOS Cumulative Capacity

        \sum_{n \in N_{r,t}} \textbf{CIECAP}_{r,p,t,n}
        =
        \sum_{\substack{r' \in R(r),\, t' \in T(t),\\ v \in V}}
            \textbf{ECAP}_{r',t',v}
        +
        \sum_{\substack{r' \in R(r),\, t' \in T(t),\\ v \le p,\, v \in \mathcal{V}(r',t')}}
            \textbf{NCAP}_{r',t',v}

        \qquad \forall \{r, p, t\} \in \Theta_{\text{cost\_invest\_eos\_period\_rpt}}

    where :math:`R(r)` and :math:`T(t)` expand any group labels to the
    individual regions and technologies they contain, and
    :math:`\mathcal{V}(r', t')` is the set of all optimised vintages for that
    process.
    """

    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    # What EOS invest thinks the cumulative capacity is for this cluster in this period
    cap_eos = quicksum(
        model.v_cost_invest_eos_cumulative_capacity[r, p, t, n]
        for n in model.cost_invest_eos_segments[r, t]
    )

    # Sum all actually built capacity so far
    cap_deployed = quicksum(
        value(model.existing_capacity[_r, _t, _v])
        for _r, _t, _v in model.existing_capacity.sparse_keys()
        if _r in regions and _t in techs
    )
    cap_deployed += quicksum(
        model.v_new_capacity[_r, _t, _v]
        for _v in model.vintage_optimize
        if _v <= p
        for _r in regions
        for _t in techs
        if (_r, _t, _v) in model.v_new_capacity
    )

    return cap_deployed == cap_eos


# --- Calculating investment costs ---
def cost_invest_eos_segment_cost(
    model: EOSModel,
    r: Region,
    t: Technology,
    n: int,
    cumulative_capacity: ExprLike,
    binary: VarData | bool = True,
) -> ExprLike:
    """Cumulative investment cost within an EOS invest segment, if capacity were in that segment"""
    cap_lower, cap_upper, cost_lower, cost_upper = model.cost_invest_eos[r, t, n]
    m = (value(cost_upper) - value(cost_lower)) / (value(cap_upper) - value(cap_lower))
    return m * cumulative_capacity + binary * (value(cost_lower) - m * value(cap_lower))


def cost_invest_eos_cluster_cumulative_cost(
    model: EOSModel, r: Region, p: Period, t: Technology
) -> Expression:
    """
    Cumulative investment cost for an EOS invest cluster up to period p,
    accounting for which segment of the cost curve is active.
    """
    return quicksum(
        cost_invest_eos_segment_cost(
            model,
            r,
            t,
            n,
            model.v_cost_invest_eos_cumulative_capacity[r, p, t, n],
            model.v_cost_invest_eos_segment_binary[r, p, t, n],
        )
        for n in model.cost_invest_eos_segments[r, t]
    )


def period_cost(model: EOSModel, r: Region, p: Period, t: Technology) -> Expression:
    r"""
    EOS invest clusters do not contribute to the base-model
    :math:`\text{CostInvest}` sum.  Instead, the extension adds a separate
    discounted-investment term to :code:`total_cost` via a
    :code:`BuildAction` (``append_cost_invest_eos_to_total_cost``).

    The *period cost* for cluster :math:`(r, p, t)` is the *incremental*
    cumulative cost: the cost of all capacity built up to period :math:`p`
    minus the cost of all capacity built up to the preceding EOS invest period
    (or the cost attributable to pre-existing capacity in the first period):

    .. math::

        \text{EOS\_Invest\_PeriodCost}_{r,p,t} =
            \mathcal{C}_{r,p,t} - \mathcal{C}_{r,p_{\text{prev}},t}

    where the cumulative cost for a cluster in a given period is:

    .. math::

        \mathcal{C}_{r,p,t} =
            \sum_{n \in N_{r,t}}
                \left[
                    m_{r,t,n} \cdot \textbf{CIECAP}_{r,p,t,n}
                    + \textbf{CIEB}_{r,p,t,n}
                        \left(\underline{C}_{r,t,n} - m_{r,t,n} \cdot \underline{K}_{r,t,n}\right)
                \right]

        \text{with slope }m_{r,p,t,n} = \dfrac{\overline{C}_{r,p,t,n} -
        \underline{C}_{r,p,t,n}}{\overline{K}_{r,p,t,n} - \underline{K}_{r,p,t,n}}

    Note the terms in this summation are only non-zero for the active segment.

    This incremental cost is then discounted and amortised using the same
    :func:`~temoa.components.costs.loan_cost` function as for cost_invest in
    the base model, using the reference process :math:`(r_0, t_0)` for loan
    parameters.  The result is added to :code:`total_cost` once per
    cluster-period combination in
    :math:`\Theta_{\text{cost\_invest\_eos\_period\_rpt}}`.
    """

    cumulative_cost = cost_invest_eos_cluster_cumulative_cost(model, r, p, t)
    prev_cum_cost: ExprLike = 0.0

    # Subtract previously accumulated investment costs to get the incremental for discounting
    prev_periods = {
        _p for _r, _p, _t in model.cost_invest_eos_period_rpt if _r == r and _t == t and _p < p
    }
    if len(prev_periods) > 0:
        # Endogenous previous cumulative investment costs to subtract
        p_prev = max(prev_periods)
        prev_cum_cost = cost_invest_eos_cluster_cumulative_cost(model, r, p_prev, t)
    else:
        # Existing capacity costs to subtract (needed for myopic)
        regions = geography.gather_group_regions(model, r)
        techs = technology.gather_group_techs(model, t)
        existing_capacity = sum(
            value(model.existing_capacity[_r, _t, _v])
            for _r, _t, _v in model.existing_capacity
            if _r in regions and _t in techs
        )
        in_bounds = False
        for n in model.cost_invest_eos_segments[r, t]:
            cap_lower, cap_upper, _, _ = model.cost_invest_eos[r, t, n]
            if value(cap_lower) <= existing_capacity <= value(cap_upper):
                prev_cum_cost = cost_invest_eos_segment_cost(model, r, t, n, existing_capacity)
                in_bounds = True
                break
        if not in_bounds:
            msg = (
                'Existing capacity for a cost_invest_eos cluster is outside the bounds of '
                'the cost curve. Check the cost_invest_eos table and existing_capacity '
                f'for {r, t}: {existing_capacity}'
            )
            logger.error(msg)
            raise ValueError(msg)

    return cumulative_cost - prev_cum_cost


def total_cost(model: EOSModel) -> None:
    """
    Discounted investment costs for all EOS invest clusters in the planning horizon
    """

    p_0 = min(model.time_optimize)
    p_e = model.time_future.last()
    global_discount_rate = value(model.global_discount_rate)

    total_cost = 0.0

    for _r, _p, _t in model.cost_invest_eos_period_rpt:
        _r0, _t0 = model.cost_invest_eos_reference_process[_r, _p, _t]
        if model.is_survival_curve_process[_r0, _t0, _p]:
            total_cost += loan_cost_survival_curve(
                model,
                _r0,
                _t0,
                _p,
                1,
                period_cost(model, _r, _p, _t),
                value(model.loan_annualize[_r0, _t0, _p]),
                value(model.loan_lifetime_process[_r0, _t0, _p]),
                p_0,
                p_e,
                global_discount_rate,
            )
        else:
            total_cost += loan_cost(
                1,
                period_cost(model, _r, _p, _t),
                value(model.loan_annualize[_r0, _t0, _p]),
                value(model.loan_lifetime_process[_r0, _t0, _p]),
                value(model.lifetime_process[_r0, _t0, _p]),
                p_0,
                p_e,
                global_discount_rate,
                vintage=_p,
            )

    # Append to total cost objective
    model.total_cost.set_value(cast('ObjectiveData', model.total_cost).expr + total_cost)
