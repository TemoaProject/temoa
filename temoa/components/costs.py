from __future__ import annotations

from typing import TYPE_CHECKING

from deprecated import deprecated
from pyomo.core import Expression, Var
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

from logging import getLogger

logger = getLogger(name=__name__)


def get_default_loan_rate(M: 'TemoaModel', *_):
    """get the default loan rate from the DefaultLoanRate param"""
    return M.DefaultLoanRate()


@deprecated(reason='vintage defaults are no longer available, so this should not be needed')
def CreateCosts(M: 'TemoaModel'):
    """
    Steps to creating fixed and variable costs:
    1. Collect all possible cost indices (CostFixed, CostVariable)
    2. Find the ones _not_ specified in CostFixed and CostVariable
    3. Set them, based on Cost*VintageDefault
    """
    logger.debug('Started Creating Fixed and Variable costs in CreateCosts()')
    # Shorter names, for us lazy programmer types
    CF = M.CostFixed
    CV = M.CostVariable

    # Step 1
    fixed_indices = set(M.CostFixed_rptv)
    var_indices = set(M.CostVariable_rptv)

    # Step 2
    unspecified_fixed_prices = fixed_indices.difference(CF.sparse_iterkeys())
    unspecified_var_prices = var_indices.difference(CV.sparse_iterkeys())

    # Step 3

    # Some hackery: We futz with _constructed because Pyomo thinks that this
    # Param is already constructed.  However, in our view, it is not yet,
    # because we're specifically targeting values that have not yet been
    # constructed, that we know are valid, and that we will need.

    if unspecified_fixed_prices:
        # CF._constructed = False
        for r, p, t, v in unspecified_fixed_prices:
            if (r, t, v) in M.CostFixedVintageDefault:
                CF[r, p, t, v] = M.CostFixedVintageDefault[r, t, v]  # CF._constructed = True

    if unspecified_var_prices:
        # CV._constructed = False
        for r, p, t, v in unspecified_var_prices:
            if (r, t, v) in M.CostVariableVintageDefault:
                CV[r, p, t, v] = M.CostVariableVintageDefault[r, t, v]
    # CV._constructed = True
    logger.debug('Created M.CostFixed with size: %d', len(M.CostFixed))
    logger.debug('Created M.CostVariable with size: %d', len(M.CostVariable))
    logger.debug('Finished creating Fixed and Variable costs')


def CostFixedIndices(M: 'TemoaModel'):
    # we pull the unlimited capacity techs from this index.  They cannot have fixed costs
    return {(r, p, t, v) for r, p, t, v in M.activeActivity_rptv if t not in M.tech_uncap}


def CostVariableIndices(M: 'TemoaModel'):
    return M.activeActivity_rptv


def annuity_to_pv(rate: float, periods: int) -> float | Expression:
    r"""
    Multiplication factor to convert an annuity to net present value

    .. math::
        :label: annuity_to_pv

        \frac{P}{A}(i, N) = \frac{(1 + i)^N - 1}{i (1 + i)^N}

    where:

    - :math:`i` is the interest/discount rate
    - :math:`N` is the number of periods
    """
    if rate == 0:
        return periods
    return ((1 + rate) ** periods - 1) / (rate * (1 + rate) ** periods)


def pv_to_annuity(rate: float, periods: int) -> float | Expression:
    r"""
    Multiplication factor to convert net present value to an annuity

    .. math::
        :label: pv_to_annuity

        \frac{A}{P}(i, N) = \frac{i + (1 + i)^N}{(1 + i)^N - 1}
    """
    if rate == 0:
        return 1 / periods
    return (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)


def fv_to_pv(rate: float, periods: int) -> float | Expression:
    r"""
    Multiplication factor to convert a future value to net present value

    .. math::
        :label: fv_to_pv

        \frac{P}{F}(i, N) = \frac{1}{(1 + i)^N}
    """
    if rate == 0:
        return 1
    return 1 / (1 + rate) ** periods


def loan_cost(
    capacity: float | Var,
    invest_cost: float,
    loan_annualize: float,
    lifetime_loan_process: float | int,
    lifetime_process: int,
    P_0: int,
    P_e: int,
    GDR: float,
    vintage: int,
) -> float | Expression:
    """
    function to calculate the loan cost.  It can be used with fixed values to produce a hard number or
    pyomo variables/params to make a pyomo Expression
    :param capacity: The capacity to use to calculate cost
    :param invest_cost: the cost/capacity
    :param loan_annualize: parameter
    :param lifetime_loan_process: lifetime of the loan
    :param P_0: the year to discount the costs back to
    :param P_e: the 'end year' or cutoff year for loan payments
    :param GDR: Global Discount Rate
    :param vintage: the base year of the loan
    :return: fixed number or pyomo expression based on input types
    """

    # calculate the amortised loan repayment (annuity)
    annuity = (
        capacity
        * invest_cost  # lump investment cost is capacity times CostInvest
        * loan_annualize  # calculate loan annuities for investment cost, if used
    )

    if not GDR:
        # Undiscounted result
        res = (
            annuity
            * lifetime_loan_process  # sum of loan payments over loan period
            / lifetime_process  # redistributed over lifetime of process
            * min(
                lifetime_process, P_e - vintage
            )  # sum of redistributed costs for life of process (within planning horizon)
        )
    else:
        # Discounted result
        res = (
            annuity
            * annuity_to_pv(
                GDR, lifetime_loan_process
            )  # PV of all loan payments, discounted to vintage year using GDR
            * pv_to_annuity(GDR, lifetime_process)  # reamortised over lifetime of process using GDR
            * annuity_to_pv(
                GDR, min(lifetime_process, P_e - vintage)
            )  # PV of all reamortised costs (within planning horizon)
            * fv_to_pv(GDR, vintage - P_0)  # finally, discounted from vintage year to P_0
        )
    return res


def loan_cost_survival_curve(
    M: 'TemoaModel',
    r: str,
    t: str,
    v: str,
    capacity: float | Var,
    invest_cost: float,
    loan_annualize: float,
    lifetime_loan_process: float | int,
    P_0: int,
    P_e: int,
    GDR: float,
) -> float | Expression:
    """
    function to calculate the loan cost only in the case of processes :math:`(r, t, v)` using
    survival curves. It can be used with fixed values to produce a hard number or pyomo
    variables/params to make a pyomo Expression
    :param capacity: The capacity to use to calculate cost
    :param invest_cost: the cost/capacity
    :param loan_annualize: parameter
    :param lifetime_loan_process: lifetime of the loan
    :param P_0: the year to discount the costs back to
    :param P_e: the 'end year' or cutoff year for loan payments
    :param GDR: Global Discount Rate
    :return: fixed number or pyomo expression based on input types
    """

    # calculate the amortised loan repayment (annuity)
    annuity = (
        capacity
        * invest_cost  # lump investment cost is capacity times CostInvest
        * loan_annualize  # calculate loan annuities for investment cost, if used
    )

    if not GDR:
        # Undiscounted result
        res = (
            annuity
            * lifetime_loan_process  # sum of loan payments over loan period
            / sum(  # redistributed over survival curve within horizon
                value(M.LifetimeSurvivalCurve[r, p, t, v])
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p
            )
            * sum(  # summed over survival curve within horizon
                value(M.LifetimeSurvivalCurve[r, p, t, v])
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p < P_e
            )
        )
    else:
        # Discounted result
        res = (
            annuity
            * annuity_to_pv(
                GDR, lifetime_loan_process
            )  # PV of all loan payments, discounted to vintage year using GDR
            / sum(  # redistributed over survival curve within horizon
                value(
                    M.LifetimeSurvivalCurve[r, p, t, v]
                )  # reamortised over survival curve of process using GDR
                * fv_to_pv(GDR, p - v + 1)  # +1 because LSC is indexed to start of p not end of p
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p  # this shouldnt be possible but play it safe
            )
            * sum(  # PV of all reamortised costs (within planning horizon)
                value(M.LifetimeSurvivalCurve[r, p, t, v]) * fv_to_pv(GDR, p - v + 1)
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p < P_e
            )
            * fv_to_pv(GDR, v - P_0)  # finally, discounted from vintage year to P_0
        )
    return res


def fixed_or_variable_cost(
    cap_or_flow: float | Var,
    cost_factor: float,
    cost_years: float,
    GDR: float | None,
    P_0: float,
    p: int,
) -> float | Expression:
    """
    Extraction of the fixed and var cost formulation.  (It is same for both with either capacity or
    flow as the driving variable.)
    :param cap_or_flow: Capacity if fixed cost / flow out if variable
    :param cost_factor: the cost (either fixed or variable) of the cap/flow variable
    :param cost_years: for how many years is this cost incurred
    :param GDR: discount rate or None
    :param P_0: the period to discount this back to
    :param p: the period under evaluation
    :return:
    """

    annual_cost = cap_or_flow * cost_factor  # annual fixed, variable, or emission cost

    if not GDR:
        # Undiscounted result
        return annual_cost * cost_years  # annual cost times years paying that cost
    else:
        # Discounted result
        return (
            annual_cost
            * annuity_to_pv(
                GDR, cost_years
            )  # PV of annual costs over this period, discounted to period p
            * fv_to_pv(GDR, p - P_0)  # discounted from p to p_0
        )


def get_loan_life(M: 'TemoaModel', r, t, v):
    return M.LifetimeProcess[r, t, v]


def LifetimeLoanProcessIndices(M: 'TemoaModel'):
    """\
Based on the Efficiency parameter's indices and time_future parameter, this
function returns the set of process indices that may be specified in the
CostInvest parameter.
"""
    min_period = min(M.vintage_optimize)

    indices = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys() if v >= min_period)

    return indices


def PeriodCost_rule(M: 'TemoaModel', p):
    P_0 = min(M.time_optimize)
    P_e = M.time_future.last()  # End point of modeled horizon
    GDR = value(M.GlobalDiscountRate)
    # MPL = M.ModelProcessLife

    if value(M.MyopicDiscountingYear) != 0:
        P_0 = value(M.MyopicDiscountingYear)

    loan_costs = sum(
        loan_cost(
            M.V_NewCapacity[r, S_t, S_v],
            value(M.CostInvest[r, S_t, S_v]),
            value(M.LoanAnnualize[r, S_t, S_v]),
            value(M.LoanLifetimeProcess[r, S_t, S_v]),
            value(M.LifetimeProcess[r, S_t, S_v]),
            P_0,
            P_e,
            GDR,
            vintage=S_v,
        )
        for r, S_t, S_v in M.CostInvest.sparse_iterkeys()
        if S_v == p and not M.isSurvivalCurveProcess[r, S_t, S_v]
    )
    loan_costs += sum(
        loan_cost_survival_curve(
            M,
            r,
            S_t,
            S_v,
            M.V_NewCapacity[r, S_t, S_v],
            value(M.CostInvest[r, S_t, S_v]),
            value(M.LoanAnnualize[r, S_t, S_v]),
            value(M.LoanLifetimeProcess[r, S_t, S_v]),
            P_0,
            P_e,
            GDR,
        )
        for r, S_t, S_v in M.CostInvest.sparse_iterkeys()
        if S_v == p and M.isSurvivalCurveProcess[r, S_t, S_v]
    )

    fixed_costs = sum(
        fixed_or_variable_cost(
            M.V_Capacity[r, p, S_t, S_v],
            value(M.CostFixed[r, p, S_t, S_v]),
            value(M.PeriodLength[p]),
            GDR,
            P_0,
            p=p,
        )
        for r, S_p, S_t, S_v in M.CostFixed.sparse_iterkeys()
        if S_p == p
    )

    variable_costs = sum(
        fixed_or_variable_cost(
            M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, S_o],
            value(M.CostVariable[r, p, S_t, S_v]),
            value(M.PeriodLength[p]),
            GDR,
            P_0,
            p,
        )
        for r, S_p, S_t, S_v in M.CostVariable.sparse_iterkeys()
        if S_p == p and S_t not in M.tech_annual
        for S_i in M.processInputs[r, S_p, S_t, S_v]
        for S_o in M.processOutputsByInput[r, S_p, S_t, S_v, S_i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    variable_costs_annual = sum(
        fixed_or_variable_cost(
            M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, S_o],
            value(M.CostVariable[r, p, S_t, S_v]),
            value(M.PeriodLength[p]),
            GDR,
            P_0,
            p,
        )
        for r, S_p, S_t, S_v in M.CostVariable.sparse_iterkeys()
        if S_p == p and S_t in M.tech_annual
        for S_i in M.processInputs[r, S_p, S_t, S_v]
        for S_o in M.processOutputsByInput[r, S_p, S_t, S_v, S_i]
    )

    # The emissions costs occur over the five possible emission sources.
    # to do any/all of them we need 2 baseline sets:  The regular and annual sets
    # of indices that are valid which is basically the filter of:
    #     EmissionActivty by CostEmission
    # and to ensure that the techology is active we need to filter that
    # result with processInput

    # ================= Emissions and Flex and Curtailment =================
    # Flex flows are deducted from V_FlowOut, so it is NOT NEEDED to tax them again.  (See commodity balance constr)
    # Curtailment does not draw any inputs, so it seems logical that curtailed flows not be taxed either
    # Earlier versions of this code had accounting for flex & curtailment that have been removed.

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in M.EmissionActivity.sparse_iterkeys()
        if (r, p, e) in M.CostEmission  # tightest filter first
        and (r, p, t, v) in M.processInputs
    ]

    # then expand the base for the normal (season/tod) set and annual separately:
    normal = [
        (r, p, e, s, d, i, t, v, o)
        for (r, p, e, i, t, v, o) in base
        for s in M.TimeSeason[p]
        for d in M.time_of_day
        if t not in M.tech_annual
    ]

    annual = [(r, p, e, i, t, v, o) for (r, p, e, i, t, v, o) in base if t in M.tech_annual]

    # 1. variable emissions
    var_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_FlowOut[r, p, s, d, i, t, v, o]
            * value(M.EmissionActivity[r, e, i, t, v, o]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=value(M.PeriodLength[p]),
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, p, e, s, d, i, t, v, o) in normal
    )

    # 2. flex emissions -- removed (double counting, flex wastes are SUBTRACTIVE from flowout)

    # 3. curtailment emissions -- removed (curtailment is no-flow, for accounting only, so no emissions)

    # 4. annual emissions
    var_annual_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_FlowOutAnnual[r, p, i, t, v, o]
            * value(M.EmissionActivity[r, e, i, t, v, o]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=value(M.PeriodLength[p]),
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, p, e, i, t, v, o) in annual
        if t not in M.tech_flex
    )

    # 5. flex annual emissions -- removed (double counting, flex wastes are SUBTRACTIVE from flowout)

    # 6. embodied - treated as a fixed cost distributed over the deployment period (vintage)
    embodied_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_NewCapacity[r, t, v]
            * value(M.EmissionEmbodied[r, e, t, v])
            / value(M.PeriodLength[p]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=M.PeriodLength[
                v
            ],  # We assume the embodied emissions are emitted in the same year as the capacity is installed.
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, e, t, v) in M.EmissionEmbodied.sparse_iterkeys()
        if (r, p, e) in M.CostEmission
        if v == p
    )

    # 6. endoflife - treated as a fixed cost distributed over the retirement period
    endoflife_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_AnnualRetirement[r, p, t, v] * value(M.EmissionEndOfLife[r, e, t, v]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=M.PeriodLength[
                p
            ],  # We assume the embodied emissions are emitted in the same year as the capacity is installed.
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, e, t, v) in M.EmissionEndOfLife.sparse_iterkeys()
        if (r, p, e) in M.CostEmission
        if (r, t, v) in M.retirementPeriods and p in M.retirementPeriods[r, t, v]
    )

    period_emission_cost = (
        var_emissions + var_annual_emissions + embodied_emissions + endoflife_emissions
    )

    period_costs = (
        loan_costs + fixed_costs + variable_costs + variable_costs_annual + period_emission_cost
    )
    return period_costs


def ParamLoanAnnualize_rule(M: 'TemoaModel', r, t, v):
    dr = value(M.LoanRate[r, t, v])
    lln = value(M.LoanLifetimeProcess[r, t, v])
    annualized_rate = pv_to_annuity(dr, lln)
    return annualized_rate


# ---------------------------------------------------------------
# Define the Objective Function
# ---------------------------------------------------------------
def TotalCost_rule(M):
    r"""

    Using the :code:`FlowOut` and :code:`Capacity` variables, the Temoa objective
    function calculates the cost of energy supply, under the assumption that capital
    costs are paid through loans. This implementation sums up all the costs incurred,
    and is defined as :math:`C_{tot} = C_{loans} + C_{fixed} + C_{variable} + C_{emissions}`.
    Each term on the right-hand side represents the cost incurred over the model
    time horizon and discounted to the initial year in the horizon (:math:`{P}_0`).
    The calculation of each term is given below.

    .. math::
        :label: obj_invest

        \begin{aligned}
            C_{loans} =& \sum_{r, t, v \in \Theta_{CI}} CI_{r, t, v} \cdot \textbf{NCAP}_{r, t, v}
            && \text{(overnight capital cost)} \\
            &\cdot \frac{A}{P}(i=\text{LR}_{r,t,v}, N=\text{LLP}_{r,t,v})
            && \text{(overnight cost amortised into annual loan payments)} \\
            &\cdot \frac{P}{A}(i=GDR, N=\text{LLP}_{r,t,v})
            && \text{(annual loan payments discounted to NPV in vintage year)} \\
            &\cdot \frac{A}{P}(i=GDR, N=\text{LTP}_{r,t,v})
            && \text{(NPV reamortised over lifetime of process using GDR)} \\
            &\cdot \frac{P}{A}(i=GDR, N=\min(\text{LTP}_{r,t,v}, P_e - v))
            && \text{(costs within planning horizon discounted to NPV in vintage year)} \\
            &\cdot \frac{P}{F}(i=GDR, N=v - P_0)
            && \text{(NPV in vintage year discounted to base year } P_0\text{)} \\
        \end{aligned}

    Note that capital costs (:math:`{CI}_{r,t,v}`) are handled in several steps.

        1. Each capital cost is amortized using the loan rate (i.e., technology-specific discount rate) and loan period.

        2. The annual stream of payments is converted into a lump sum using the global discount rate and loan period.

        3. The new lump sum is amortized at the global discount rate over the process lifetime.

        4. Loan payments beyond the model time horizon are removed and the lump sum recalculated.

        5. Finally, the lump sum is discounted back to the beginning of the horizon (:math:`P_0`) using the global discount rate.

    Steps 3 and 4 serve to correctly balance the cost-benefit of technologies whose useful lives
    would extend beyond the planning horizon. While an explicit salvage term is not included, this approach properly
    captures the capital costs incurred within the model time horizon, accounting for process-specific loan rates
    and periods.

    In the case of processes using survival curves, steps 3 and 4 do not reamortise costs uniformly over the process lifetime.
    Instead, costs are amortised over the life of the process in proportion to the survival fraction in each year.
    Note that, for this calculation, a survival curve :math:`{LSC}_{r,y,t,v}` must be defined out to the year in which the
    surviving fraction is zero, even if that extends beyond the planning horizon. It must also be defined for each integer
    year between model periods and, if not, these gaps will be filled by linear interpolation ahead of this calculation.

    .. math::
        :label: obj_invest_survival_curve

        \begin{aligned}
            C_{loans,LSC} =& \sum_{r, t, v \in \Theta_{CI}} CI_{r, t, v} \cdot \textbf{NCAP}_{r, t, v}
            && \text{(overnight capital cost)} \\
            &\cdot \frac{A}{P}(i=\text{LR}_{r,t,v}, N=\text{LLP}_{r,t,v})
            && \text{(overnight cost amortised into annual loan payments)} \\
            &\cdot \frac{P}{A}(i=GDR, N=\text{LLP}_{r,t,v})
            && \text{(annual loan payments discounted to NPV in vintage year)} \\
            &\cdot \left(
                \sum_{v < Y} LSC_{r,y,t,v} \cdot \frac{P}{F}(i=GDR, N=P - v + 1)
                \right)^{-1}
            && \text{(reamortised over survival curve (normalized)} \\
            &\cdot \sum_{v < Y < P_e} LSC_{r,y,t,v} \cdot \frac{P}{F}(i=GDR, N=P - v + 1)
            && \text{(costs within planning horizon discounted to NPV in vintage year)} \\
            &\cdot \frac{P}{F}(i=GDR, N=v - P_0)
            && \text{(NPV in vintage year discounted to base year } P_0 \text{)}
        \end{aligned}

    Where :math:`Y` is the set of each integer year :math:`y` within the planning horizon.

    .. figure:: images/survival_curve_discounting.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 60%

        Steps 3 and 4 for processes with survival curves.

    Fixed, variable, and emissions annual cost factors are determined by:

    .. math::
       :label: annual_fixed_variable_emission

        \begin{aligned}
            C_{fixed} =& \sum_{r, p, t, v \in \Theta_{CF}} CF_{r, p, t, v} \cdot \textbf{CAP}_{r, p, t, v}
            && \text{(annual fixed cost)} \\
            \\
            C_{variable} =& \sum_{r, p, t \notin T^a, v \in \Theta_{CV}}
            CV_{r, p, t, v} \cdot \sum_{S, D, I, O} \mathbf{FO}_{r, p, s, d, i, t, v, o}
            && \text{(annual variable cost on flow)} \\
            & \text{where } t \notin T^a \\
            &+\\
            & \sum_{r, p, t \in T^a,\ v \in \Theta_{VC}} CV_{r, p, t, v}
            \cdot \sum_{I, O} \mathbf{FOA}_{r, p, i, t, v, o}
            && \text{(annual variable cost on annual flows)} \\
            & \text{where } t \in T^a \\
            &+\\
            C_{emissions} =& \sum_{r, p, e \in \Theta_{CE}} CE_{r, p, e}
            \cdot EAC_{r, i, t, v, o, e} \cdot \sum_{S, D, I, O} \mathbf{FO}_{r, p, s, d, i, t, v, o}
            && \text{(annual emission cost on flow)} \\
            & \text{where } t \notin T^a \\
            &+\\
            & \sum_{r, p, e \in \Theta_{CE}} CE_{r, p, e}
            \cdot EAC_{r, i, t, v, o, e} \cdot \sum_{I, O} \mathbf{FOA}_{r, p, i, t, v, o}
            && \text{(annual emission cost on annual flows)} \\
            & \text{where } t \in T^a \\
            &+\\
            & \sum_{r, p, e \in \Theta_{CE}} \frac{CE_{r, p, e}
            \cdot EE_{r, e, t, v} \cdot \mathbf{NCAP}_{r, t, v=p}}{{LEN}_p}
            && \text{(annual embodied emission cost)} \\
            &+\\
            & \sum_{r, p, e \in \Theta_{CE}, v} CE_{r, p, e}
            \cdot EEOL_{r, e, t, v} \cdot \mathbf{ART}_{r, p, t, v}
            && \text{(annual retirement/end of life emission cost)} \\
        \end{aligned}

    Each of these costs are then discounted within each period and then to the base year:

    .. math::
        :label: obj_fixed_variable_emission

        \begin{aligned}
            C_{fix,var,emiss} =& C_{fixed} + C_{variable} + C_{emissions} \\
            &\cdot \frac{P}{A}(i=GDR,\ N=LEN_p)
            && \text{(for each year in period } p \text{ discounted to NPV in } p \text{)}\\
            &\cdot \frac{P}{F}(i=GDR,\ N=p - P_0)
            && \text{(discounted from period } p \text{ to NPV in base year } P_0 \text{)}
        \end{aligned}
    """

    return sum(PeriodCost_rule(M, p) for p in M.time_optimize)
