from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pyomo.environ import quicksum, value

from temoa.components import capacity
from temoa.components.costs import fixed_or_variable_cost

if TYPE_CHECKING:
    from pyomo.core import Expression
    from pyomo.core.base.objective import ObjectiveData
    from pyomo.core.base.var import VarData

    from temoa.extensions.economies_of_scale.core.model import EOSModel
    from temoa.types import ExprLike, Period, Region, Technology

logger = logging.getLogger(__name__)


def period_cost_indices(model: EOSModel) -> set[tuple[Region, Period, Technology]]:
    return {(r, p, t) for r, p, t, _ in model.cost_variable_eos_rptn}


def initialize_components(model: EOSModel) -> None:
    """
    Organise some data and put up some guard rails
    """

    # Collect segment indices n for each (r,p,t) cluster; order doesn't matter
    for r, p, t, n in model.cost_variable_eos_rptn:
        model.cost_variable_eos_segments.setdefault((r, p, t), set()).add(n)

    # Check that costs and activities are monotonically increasing
    for (r, p, t), segs in model.cost_variable_eos_segments.items():
        sorted_segs = sorted(segs)
        for i, n in enumerate(sorted_segs):
            act_lower, act_upper, cost_lower, cost_upper = model.cost_variable_eos[r, p, t, n]

            # Check cost curve is nonnegative and monotonically increasing
            # If someone wants to break this assumption they should have the
            # skills to edit this code.
            if not all(
                (
                    act_lower >= 0,
                    act_upper >= 0,
                    cost_lower >= 0,
                    cost_upper >= 0,
                    act_upper > act_lower,
                    cost_upper > cost_lower,
                )
            ):
                msg = (
                    'Negative values or non-increasing segment bounds found '
                    f'in cost_variable_eos table for {r, p, t, n}'
                )
                logger.error(msg)
                raise ValueError(msg)

            # Backcheck for monotonic growth
            if i == 0:
                continue

            _, prev_act_upper, _, prev_cost_upper = model.cost_variable_eos[
                r, p, t, sorted_segs[i - 1]
            ]

            if not all(
                (
                    abs(act_lower - prev_act_upper) <= 0.001,
                    abs(cost_lower - prev_cost_upper) <= 0.001,
                )
            ):
                msg = (
                    'Segments in cost_variable_eos table do not align on their bounds. This would '
                    'leave gaps in the cost curve and could lead to infeasibility. Check '
                    f'({r, p, t, sorted_segs[i - 1]}) to ({r, p, t, n})'
                )
                logger.error(msg)
                raise ValueError(msg)


# --- Enforce the rules of activity progression up the cost curve ---
def cost_variable_eos_segment_binary_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    r"""
    Enforce exactly one active segment of the cost curve for each cluster
    in each period.

    Each technology cluster :math:`(r, p, t)` has a piecewise-linear cost curve
    split into :math:`N_{r,p,t}` segments.  The binary variable
    :math:`\textbf{CVEB}_{r,p,t,n}` selects which segment is currently active.
    Exactly one segment must be active at all times:

    .. math::
        :label: Cost Variable EOS Segment Binary Constraint

        \sum_{n \in N_{r,p,t}} \textbf{CVEB}_{r,p,t,n} = 1

        \qquad \forall \{r, p, t\} \in \Theta_{\text{cost\_variable\_eos\_period\_rpt}}

    where :math:`\textbf{CVEB}_{r,p,t,n}` is
    :code:`v_cost_variable_eos_segment_binary[r, p, t, n]` (:math:`\in \{0, 1\}`) and
    :math:`N_{r,p,t}` is the set of segment indices declared for cluster
    :math:`(r, p, t)` in the :code:`cost_variable_eos` table.
    """
    count_active_segments = quicksum(
        model.v_cost_variable_eos_segment_binary[r, p, t, n]
        for n in model.cost_variable_eos_segments[r, p, t]
    )
    return count_active_segments == 1


def cost_variable_eos_activity_lower_bound_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology, n: int
) -> ExprLike:
    r"""
    Enforce the lower bound of the active EOS cost-curve segment on the
    activity variable for that segment.

    When segment :math:`n` is inactive (:math:`\textbf{CVEB}_{r,p,t,n} = 0`), the
    right-hand side collapses to zero so the constraint is non-binding.  When
    segment :math:`n` is active (:math:`\textbf{CVEB}_{r,p,t,n} = 1`), it
    enforces that the segment activity is at least the lower boundary
    :math:`\underline{A}_{r,p,t,n}` of that segment:

    .. math::
        :label: Cost Variable EOS Activity Lower Bound

        \textbf{CVEACT}_{r,p,t,n}
            \ge \textbf{CVEB}_{r,p,t,n} \cdot \underline{A}_{r,p,t,n}

        \qquad \forall \{r, p, t, n\} \in \Theta_{\text{cost\_variable\_eos\_rptn}}

    where :math:`\textbf{CVEACT}_{r,p,t,n}` is
    :code:`v_cost_variable_eos_activity[r, p, t, n]`, :math:`\textbf{CVEB}_{r,p,t,n}`
    is :code:`v_cost_variable_eos_segment_binary[r, p, t, n]`, and
    :math:`\underline{A}_{r,p,t,n}` is :code:`cost_variable_eos[r, p, t, n][0]`
    (the :code:`activity_lower` column).
    """
    act_lower = model.v_cost_variable_eos_segment_binary[r, p, t, n] * value(
        model.cost_variable_eos[r, p, t, n][0]
    )
    return model.v_cost_variable_eos_activity[r, p, t, n] >= act_lower


def cost_variable_eos_activity_upper_bound_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology, n: int
) -> ExprLike:
    r"""
    Enforce the upper bound of the active EOS cost-curve segment on the
    activity variable for that segment.

    This is the mirror of the lower bound.  When segment :math:`n` is inactive
    the right-hand side collapses to zero, driving
    :math:`\textbf{CVEACT}_{r,p,t,n}` to zero.  When it is active,
    the segment activity cannot exceed the upper boundary
    :math:`\overline{A}_{r,p,t,n}` of that segment:

    .. math::
        :label: Cost Variable EOS Activity Upper Bound

        \textbf{CVEACT}_{r,p,t,n}
            \le \textbf{CVEB}_{r,p,t,n} \cdot \overline{A}_{r,p,t,n}

        \qquad \forall \{r, p, t, n\} \in \Theta_{\text{cost\_variable\_eos\_rptn}}

    where :math:`\overline{A}_{r,p,t,n}` is :code:`cost_variable_eos[r, p, t, n][1]`
    (the :code:`activity_upper` column).

    Together the lower and upper bound constraints implement a "big-M"-style
    activation: only the single active segment can carry non-zero activity,
    and that activity is pinned within the segment's range.
    """
    act_upper = model.v_cost_variable_eos_segment_binary[r, p, t, n] * value(
        model.cost_variable_eos[r, p, t, n][1]
    )
    return model.v_cost_variable_eos_activity[r, p, t, n] <= act_upper


def cost_variable_eos_activity_constraint(
    model: EOSModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    r"""
    Equate the EOS activity expression to the actual total activity in the
    base model.

    The EOS formulation tracks activity internally through
    :math:`\textbf{CVEACT}_{r,p,t,n}`.  This constraint ties those
    internal variables to the real flow decision variables from the base
    Temoa model, so the cost curve reflects actual activity rather than
    a free parameter:

    .. math::
        :label: Cost Variable EOS Activity

        \sum_{n \in N_{r,p,t}} \textbf{CVEACT}_{r,p,t,n}
        =
        \sum_{\substack{r' \in R(r),\, t' \in T(t) \setminus T_a,\\
                         v,\, s,\, d,\, i,\, o}}
            \textbf{FO}_{r',p,s,d,i,t',v,o}
        +
        \sum_{\substack{r' \in R(r),\, t' \in T(t) \cap T_a,\\
                         v,\, i,\, o}}
            \textbf{FOA}_{r',p,i,t',v,o}

        \qquad \forall \{r, p, t\} \in \Theta_{\text{cost\_variable\_eos\_period\_rpt}}

    where :math:`R(r)` and :math:`T(t)` expand any group labels to the
    individual regions and technologies they contain, :math:`T_a` is the set
    of annual technologies (:code:`tech_annual`),
    :math:`\textbf{FO}` is :code:`v_flow_out` summed over all vintages,
    seasons :math:`s`, times of day :math:`d`, inputs :math:`i`, and outputs
    :math:`o` active in period :math:`p`, and :math:`\textbf{FOA}` is
    :code:`v_flow_out_annual` for annual technologies (no :math:`s,d` indices).
    """

    activity_eos = quicksum(
        model.v_cost_variable_eos_activity[r, p, t, n]
        for n in model.cost_variable_eos_segments[r, p, t]
    )
    activity = quicksum(
        model.v_flow_out[_r, p, s, d, S_i, _t, S_v, S_o]
        for _r, _t in capacity.gather_group_active_processes(model, r, p, t)
        if _t not in model.tech_annual
        for S_v in model.process_vintages.get((_r, p, _t), [])
        for S_i in model.process_inputs[_r, p, _t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, _t, S_v, S_i]
        for s in model.time_season
        for d in model.time_of_day
    )
    activity += quicksum(
        model.v_flow_out_annual[_r, p, S_i, _t, S_v, S_o]
        for _r, _t in capacity.gather_group_active_processes(model, r, p, t)
        if _t in model.tech_annual
        for S_v in model.process_vintages.get((_r, p, _t), [])
        for S_i in model.process_inputs[_r, p, _t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, _t, S_v, S_i]
    )
    return activity == activity_eos


# --- Calculating costs ---
def cost_variable_eos_segment_cost(
    model: EOSModel,
    r: Region,
    p: Period,
    t: Technology,
    n: int,
    activity: ExprLike,
    binary: VarData | bool = True,
) -> ExprLike:
    """Variable cost within a segment, if activity were in that segment"""
    act_lower, act_upper, cost_lower, cost_upper = model.cost_variable_eos[r, p, t, n]
    m = (value(cost_upper) - value(cost_lower)) / (value(act_upper) - value(act_lower))
    return m * activity + binary * (value(cost_lower) - m * value(act_lower))


def period_cost(model: EOSModel, r: Region, p: Period, t: Technology) -> Expression:
    r"""
    EOS clusters do not contribute to the base-model
    :math:`\text{CostVariable}` sum.  Instead, the extension adds a separate
    discounted variable-cost term to :code:`total_cost` via a
    :code:`BuildAction` (``append_cost_variable_eos_to_total_cost``).

    The *period cost* for cluster :math:`(r, p, t)` is evaluated from the
    piecewise-linear cost curve at the total activity in period :math:`p`:

    .. math::

        \text{EOS\_PeriodCost}_{r,p,t} =
            \sum_{n \in N_{r,p,t}}
                \left[
                    m_{r,p,t,n} \cdot \textbf{CVEACT}_{r,p,t,n}
                    + \textbf{CVEB}_{r,p,t,n}
                        \left(\underline{C}_{r,p,t,n} - m_{r,p,t,n}
                        \cdot \underline{A}_{r,p,t,n}\right)
                \right]

        \text{with slope }m_{r,p,t,n} = \dfrac{\overline{C}_{r,p,t,n} -
        \underline{C}_{r,p,t,n}}{\overline{A}_{r,p,t,n} - \underline{A}_{r,p,t,n}}

    Note the terms in this summation are only non-zero for the active segment.

    This cost is then discounted and amortised using the same
    :func:`~temoa.components.costs.fixed_or_variable_cost` function as for
    cost_variable in the base model.  The result is added to :code:`total_cost`
    once per cluster-period combination in
    :math:`\Theta_{\text{cost\_variable\_eos\_period\_rpt}}`.
    """
    return quicksum(
        cost_variable_eos_segment_cost(
            model,
            r,
            p,
            t,
            n,
            model.v_cost_variable_eos_activity[r, p, t, n],
            model.v_cost_variable_eos_segment_binary[r, p, t, n],
        )
        for n in model.cost_variable_eos_segments[r, p, t]
    )


def total_cost(model: EOSModel) -> None:
    """
    Discounted fixed costs for all EOS clusters in the planning horizon
    """

    p_0 = min(model.time_optimize)
    global_discount_rate = value(model.global_discount_rate)

    total_cost = quicksum(
        fixed_or_variable_cost(
            1,
            period_cost(model, r, p, t),
            value(model.period_length[p]),
            global_discount_rate,
            p_0,
            p=p,
        )
        for r, p, t in model.cost_variable_eos_period_rpt
    )

    # Append to total cost objective
    model.total_cost.set_value(cast('ObjectiveData', model.total_cost).expr + total_cost)
