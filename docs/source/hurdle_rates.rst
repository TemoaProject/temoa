Investment hurdle rates
=======================

A buyer may prefer cheaper equipment even when a more efficient option would
cost less over its life. Increasing the loan rate to represent that preference
also increases reported financing costs. The optional :code:`hurdle_rate` input
separates these two effects: it weights new investment in the choice objective
without treating the extra weight as spending.

Input and calculation
---------------------

:code:`hurdle_rate` follows :code:`loan_rate`: its index is
:code:`(region, tech, vintage)`, using the model's :code:`cost_invest_rtv` set.
Its optional database table has columns :code:`region`, :code:`tech`,
:code:`vintage`, :code:`rate`, and :code:`notes`, with the same primary key and
technology/vintage references as :code:`loan_rate`. The loader uses the same
:code:`viable_rtv_new` filter; Pyomo validates nonnegative values and membership
in the investment index set. Under source tracing and myopic loading, rows for
existing or unavailable processes are filtered in the same way as loan rates.
In unfiltered loading, invalid investment indices are rejected.

This form allows the same financing and buying assumptions to be specified for
each new process. Missing rows, an empty table, or an absent table all mean zero.
There is no separate metadata default: an opt-in, process-specific input avoids
silently applying buying preferences to every investment. Existing databases do
not need migration to run unchanged. To use the feature, add the optional table
from :code:`temoa_schema_v4.sql`.

A rate of :code:`0.10` adds ten percentage points. With loan rate :math:`r`,
hurdle :math:`h`, and loan life :math:`L`, the investment weight is

.. math::

   w = \frac{\operatorname{CRF}(r+h,L)}{\operatorname{CRF}(r,L)}, \qquad
   \operatorname{CRF}(i,L) = \frac{i}{1-(1+i)^{-L}}, \qquad
   \operatorname{CRF}(0,L) = 1/L.

The model retains :code:`loan_annualize` at the real loan rate and calculates
:code:`investment_choice_annualize` at :code:`loan_rate + hurdle_rate`. When
the hurdle is zero it reuses the original loan annuity exactly. Both ordinary
and survival-curve investment terms use the choice annuity in the objective.
Loan life, process life, survival shares, horizon truncation, and discounting
are otherwise unchanged. The hurdle is not charged on existing capacity.

Fuel, fixed, variable, emissions, and unit-commitment startup costs retain their
original coefficients. The global discount rate is unchanged. Economies-of-scale
investment curves use the same annuity ratio; processes sharing a curve must
also share a hurdle rate, just as they must share their financing assumptions.

Costs and choice scores
-----------------------

:code:`output_cost` keeps its existing meaning. In particular, :code:`INVEST`
and :code:`D_INVEST` value the quantities actually bought at the real loan rate.
A hurdle can change those quantities and therefore change real system costs.

In :code:`output_objective`, the :code:`total_cost` row's
:code:`total_system_cost` value is real discounted system cost. With an active
nonzero hurdle, a second row named :code:`choice_score` holds the penalized
objective value in the same legacy numeric column. Do not sum these rows.
When all eligible hurdles are zero, the extra row is omitted to preserve the
existing output layout; the choice score then equals the model's real cost.

.. code-block:: sql

   SELECT scenario, total_system_cost
   FROM output_objective
   WHERE objective_name = 'total_cost';

The reconciliation is:

.. math::

   \text{choice score} = \text{real discounted cost} + \text{investment hurdle penalty}.

The model component :code:`total_cost` remains the optimization objective for
API compatibility. :code:`real_cost` is the separate accounting expression.
Both include interregional links and enabled cost extensions. Perfect-foresight
reporting evaluates the real-cost expression for :code:`total_cost`. Myopic
reporting preserves its existing calculation: the sum of :code:`D_INVEST`,
:code:`D_FIXED`, :code:`D_VAR` and :code:`D_EMISS` in :code:`output_cost`.
The exchange cost ledger already includes link variable costs.

Myopic runs retain model choice scores for the same periods kept in the output
tables. A later window replaces overlapping forecasts; a rollback discards the
replaced periods. Investments remain assigned to their vintage and use that
solve window's horizon, preserving the existing myopic loan accounting. The
final score is for the retained sequence, not the sum of overlapping window
objectives or the last window's objective. The choice score includes costs even
when output thresholds omit their detailed rows; the reported myopic cost total
retains its existing dependence on those rows. The reconciliation above uses
the full model cost, before any output filtering.

Shadow prices include the hurdle because they are derived from the choice
objective. They are marginal choice values, not necessarily financial prices.

Worked example
--------------

One unit of service can be supplied by standard equipment costing 1,000 with
annual operation of 300, or efficient equipment costing 1,500 with annual
operation of 240. Equipment and loans last 15 years, the loan rate is 5%, and
the global discount rate is 2%. All payments occur at year end.

With no hurdle, efficient equipment wins. With a ten-point hurdle, standard
equipment wins. Its reported annual equivalent cost is 396.34; the annual
equivalent choice score is 471.02. Discounted over the full life, reported cost
is 5,092.71, the choice score is 6,052.22, and the excluded penalty is 959.52.
The actual extra cost of choosing standard instead of efficient is 151.99.

Other objective users
---------------------

* MGA and single-vector MGA keep their near-optimality constraint on the choice
  score, including the hurdle. Log messages identify that quantity explicitly.
  The single-vector summary reports real costs for both solutions; its active
  alternative objective remains separately identified. Existing configuration
  names such as :code:`cost_epsilon` are retained.
* Monte Carlo workers use the shared output reader, so their results carry both
  metrics when appropriate. The example cost analyzer selects :code:`total_cost`
  explicitly to avoid mixing scores into its cost distribution.
* Both Method of Morris evaluators select the :code:`total_cost` row explicitly;
  their cost response remains real cost. The evaluator's log and the legacy
  example's export label now say so.
* Stochastic first-stage accounting uses the period choice expression, including
  the hurdle and cost extensions. Its expected objective remains a choice score;
  scenario reporting uses the common real-cost reader.
* The unit-cost explorer uses the real-cost expression.

Regression evidence
-------------------

Before any model or reporting code changed, every output table and the
objective of Utopia, test_system, Mediumville, seasonal_storage, survival_curve,
annualised_demand and myopic Utopia were saved at :code:`d5148dbb`. After the
change, each case was solved again with an empty hurdle table, a missing table
and explicit zero rows, on the same machine. All of them matched.

In the test suite, the existing full-run tests check the objectives of these
cases as before, and a new test solves Utopia with an empty, missing and all-zero
hurdle table and checks each result against Utopia's recorded objective. Additional
small Gurobi tests check the worked example, different loan and process lives,
zero interest and discount rates, truncated horizons, declining survival curves,
existing capacity, economies of scale, overlapping myopic windows, operating/link
cost reporting, shadow prices, and the Monte Carlo, Morris and single-vector MGA
reporting paths.
