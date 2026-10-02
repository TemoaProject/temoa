# Electricity Shadow Prices from Temoa: What the Duals Mean and How to Use Them

## Purpose

Temoa is a linear-programming capacity-expansion model. When it is solved, every constraint
comes with a *dual value*, also called a shadow price. The dual on the electricity balance
constraint is the natural place to look for the marginal cost of electricity supply: how much
total system cost would rise if one more unit of electricity had to be supplied in a given
region, period and time slice.

The raw duals Temoa writes out are not directly usable as prices. They are expressed in the
units of Temoa's objective function, which discounts every cost back to a base year and adds
up costs over all years of each multi-year period. They also depend on the time-slice
structure, on whether the model was run with perfect foresight or myopically, and on how
capital costs are spread over time in the objective.

This document explains:

1. what the raw electricity duals mean in Temoa;
2. what costs they include, in perfect-foresight and myopic runs, using a new gas turbine as a
   worked example;
3. how the companion script `scripts/electricity_prices.py` turns them into estimated marginal
   prices in $/MWh by region, period and time slice;
4. the caveats to keep in mind when reading those prices;
5. how those marginal prices compare with the average cost of electricity computed from
   Temoa's cost outputs.

Everything here was checked against the Temoa source code (repo commit `fc10702d`) and the
`temoa_power.sqlite` input database. Numerical claims were tested by solving small cases on
copies of Temoa's Utopia tutorial database. A small stand-alone example model is in
`scripts/reserve_dual_toy.py`.

---

## 1. What the raw electricity duals mean

### 1.1 A quick refresher on duals

In a cost-minimizing linear program, the dual of a constraint tells you how much the optimal
objective would change if that constraint's right-hand side were loosened or tightened by one
unit, with everything else free to adjust. For a supply–demand balance, "tighten by one unit"
means "serve one more unit of demand." The dual is therefore the system's marginal cost of
supplying that commodity, at that place and time.

Two features of Temoa determine how to read that number: which constraint is the electricity
balance, and how the objective function measures cost.

### 1.2 Which constraint balances electricity

In `temoa_power`, electricity passes through several commodities. Generators produce `ELCP`,
which can be thought of as busbar electricity. A loss technology, `E_ELCTDLOSS` (efficiency
0.953), converts `ELCP` to `ELC`. `ELC` is the regional grid node. Storage (`E_Batt`,
`E_Batt8hr`, `E_HYDPS_R`), interregional transmission (`E_TRANS_N`, `E_TRANS_R`), and the
technologies that deliver electricity to the residential, commercial and transport sectors all
connect at `ELC`. `ELC` is therefore the most natural place to measure the price of grid
electricity, and it is the script's default.

Both `ELC` and `ELCP` are ordinary physical commodities in Temoa's classification: they are
neither "annual" nor "waste" commodities. Temoa therefore balances them with
**`commodity_balance_constraint[r, p, s, d, c]`** (`temoa/components/commodities.py`). This is
an equality, `produced == consumed`, written separately for every region r, period p, season s
and time of day d. Other balance-type constraints apply to different kinds of commodity:

- `demand_constraint` applies only to end-use demand commodities.
- `annual_commodity_balance_constraint` applies only to commodities balanced over a whole
  year.
- Waste commodities use an inequality instead of an equality.

None of these applies to grid electricity.

### 1.3 What a time slice represents

`temoa_power` has two seasons, covering 62.4% and 37.6% of the year. Each season has 96
time-of-day entries, and each entry is a single representative hour. That gives 192 slices per
region and period. (The `hours` column in the `time_of_day` table is 0.25 for every entry, but
Temoa uses it only as a relative weight: each hour receives an equal 1/96 share of its season.)
Because 192 representative hours stand in for all 8,760 hours of the year, each slice is
weighted to represent many real hours: about 57 hours per year for each `S1` hour, and about
34 for each `S2` hour.

Temoa's flow variables measure **energy over the whole slice for one representative year**,
not power. This follows from the capacity constraint, `output ≤ CF × C2A × SEG × capacity`,
where SEG is the slice's fraction of the year. The electricity balance is therefore written
in PJ per slice-year. Its dual is the cost of consuming one extra PJ in that slice, **in every
year of the period**. Because the flows already measure energy over the slice, there is no
need to divide by the slice's length to get a per-energy price.

### 1.4 Sign

Temoa's modeling layer (Pyomo) stores the balance as `produced − consumed = 0` and reports each
dual as the change in the objective per unit increase in the right-hand side. Raising the
right-hand side means production must exceed consumption, which is the same as adding load.
So for this cost-minimizing model, **a positive dual means a positive marginal cost**, and no
sign flip is needed.

This was confirmed on the Utopia test database solved with Gurobi. Fuel balance duals came out
positive, and for a fuel whose marginal source is an import with a fixed cost of 2.0 M$/PJ, the
dual divided by the discount factor (§1.6) came back as exactly 2.0000 in every period.

Because the balance is an equality, the dual can still be negative in some slices. Section 4
explains when that happens.

### 1.5 Where duals are stored, and in what units

When a run is made with `save_duals = true`, Temoa writes duals to the output table
`output_dual_variable(scenario, constraint_name, dual)`. They are raw solver values, keyed by
strings such as `commodity_balance_constraint[CA,2030,S1,H5,ELC]`.

The units are those of the objective function divided by those of the commodity. For
`temoa_power` that is **millions of dollars, discounted to 2020, per PJ**.

Perfect-foresight runs store duals under the scenario name. Myopic runs store them separately
for each window, under `<scenario>-<window start year>`; see §3.

### 1.6 How Temoa's objective discounts costs

Temoa's objective (`temoa/components/costs.py`) is the total discounted cost of the energy
system. Costs that recur every year, such as fuel, variable and fixed O&M, and emission
charges, are calculated for a single representative year of each period. They are then
multiplied by a **period discount factor**:

```
DF_p = (sum over the years of period p of each year's discount factor)
     = Σ_{k = 1 .. LEN_p} (1 + r)^−(p − P0 + k)
```

where:

- **r** is the global discount rate, 2% in `temoa_power`.
- **P0** is the base year, 2020: the first optimized period. In myopic runs Temoa uses the
  first future period for every window, so P0 is also 2020 there.
- **LEN_p** is the period length: the gap to the next period. Every period from 2020 to 2050 is
  five years long. The final 2055 entry only marks the end of the horizon and sets the length
  of the last period.

The convention is **end of year**: the first year of each period is already discounted by one
full year, with no mid-year adjustment. For `temoa_power`:

| Period | 2020 | 2025 | 2030 | 2035 | 2040 | 2045 | 2050 |
|---|---|---|---|---|---|---|---|
| DF_p | 4.713 | 4.269 | 3.867 | 3.502 | 3.172 | 2.873 | 2.602 |

Because the dual is the change in this discounted, multi-year objective, it carries the same
factor. **Dividing a dual by DF_p converts it back to an ordinary cost per unit in a single
year of period p, in undiscounted dollars.** This is the key step in turning duals into
prices.

Capital costs are handled differently. The overnight cost of new capacity is first converted
into loan payments at a technology-specific loan rate. That stream of payments is converted to
a present value and spread evenly over the plant's lifetime at the global discount rate.
**Only the payments that fall before the end of the model horizon are charged.** In perfect
foresight the horizon ends in 2055; in myopic runs it is the end of the current window. This
is the standard way to avoid charging the model for years it cannot see, and it matters for
the discussion of myopic runs below.

---

## 2. What the duals include: a gas turbine example

### 2.1 The electricity dual already includes every other constraint

It is natural to ask whether the electricity balance dual captures everything, or whether you
also need the duals on the reserve-margin constraint, emission caps and so on. **The balance
dual already captures everything.** When the model must supply a little more electricity in a
slice, the solver re-optimizes everything to meet it: dispatch, storage, imports, new
investment, and every constraint those decisions touch. The dual is the total cost of that
cheapest response, including all knock-on effects.

The optimality conditions of the linear program show how the pieces fit together. Suppose a
gas turbine supplies the extra electricity in a peak slice. At the optimum:

```
λ_ELC = DF_p × VOM + λ_gas / η + μ_cap + (1 + PRM) × ρ_reserve + EF × π_CO2 + …
```

where:

- **λ_ELC** is the raw dual of the `ELC` balance in that slice.
- **λ_gas** is the dual of the balance for the gas the turbine burns (`E_NGA`, also balanced
  per slice): the model's own marginal cost of gas in that slice. It is divided by the
  efficiency η (0.351) because one PJ of electricity needs 2.85 PJ of gas.
- **μ_cap** is the dual of the turbine's capacity constraint, which is nonzero only when the
  turbine is running flat out.
- **ρ_reserve** is the dual of the planning reserve-margin constraint in that slice. The
  reserve requirement is 1 + PRM times the output of reserve-eligible plants, so one more PJ
  from the turbine raises the requirement by 1.35 PJ with a 35% margin.
- **π_CO2** is the dual of any binding emissions limit, multiplied by the turbine's emissions
  per PJ (EF).

Every term is in the same discounted units. Only VOM shows an explicit `DF_p`, because the
objective's cost coefficients are discounted while the duals come out discounted
automatically.

The practical conclusion is that **you should not add the reserve-margin or emission duals to
the electricity dual; that would count them twice.** Those other duals are useful only for
breaking the price into its parts (energy, capacity, carbon, renewable mandates), for example
to explain why a slice is expensive.

### 2.2 Which of the turbine's costs end up in the price

Suppose a peak slice needs new capacity, and the cheapest option is a new gas turbine
(`E_NGAACT_N`). The inputs used here are for Texas, 2030 vintage:

- overnight cost 733 M$/GW;
- loan rate 3.9% over a 15-year loan; plant lifetime 50 years;
- fixed O&M 20.5 M$/GW-yr; variable O&M 1.35 M$/PJ (about 4.85 $/MWh);
- efficiency 0.351;
- capacity credit 0.9;
- a 35% planning reserve margin.

The loan rate, loan life and lifetime were read from other regions' rows and assumed to apply
to Texas.

After dividing by the discount factor, the price in that slice breaks down as:

```
price = running cost + (yearly capital payment + fixed O&M) × k / (slice-years of energy per GW)
```

**Running cost.** This is the variable O&M, plus fuel at the model's own gas price divided by
the efficiency, plus any emission charges.

**Capital, as a yearly payment.** The overnight cost never enters the price directly. Temoa
converts it into an even yearly payment: here, about **26.8 M$/GW per year**. In a myopic run
with one-period windows, the objective charges exactly five years of these payments, and
dividing by the discount factor recovers one year's payment. Adding fixed O&M gives about
**47.3 M$/GW-yr**.

**Spreading it over very few hours.** A GW of capacity can deliver only about 57 GWh per year in
an `S1` slice, because the slice covers only about 57 hours. One extra PJ in that slice
therefore needs about 4.9 GW of extra capacity, and the yearly capacity cost is spread over a
small amount of energy:

- **If the turbine's own capacity limit is what binds (k = 1),** the capacity cost adds about
  **830 $/MWh** to the price in that slice.
- **If the reserve margin binds first,** which is likely with a 35% margin, each extra unit of
  output needs 1.35 units of reserve, and each GW counts at its 0.9 capacity credit, so
  k ≈ 1.35 / 0.9 = 1.5. The capacity cost then adds about **1,245 $/MWh**. In this case the
  capacity cost reaches the electricity price through the reserve dual, not the turbine's
  capacity dual. (Under Temoa's "dynamic" reserve method, the turbine's availability in that
  slice replaces the capacity credit.)

For comparison, spreading the full overnight cost over one year of that slice would give about
12,900 $/MWh. The dual never does that, because it carries yearly payments, not the lump sum.

These figures are approximate: they assume a single binding slice and the Texas 2030 inputs.
They do, however, explain why peak-slice prices in the thousands of dollars per MWh are normal
in a model like this.

### 2.3 What about capacity built in earlier periods?

A related question is whether the capital cost of plants built in earlier periods should ever
appear in a later period's price. The answer depends **not on when the plant was built, but on
whether its size was a decision in the same model solve that produced the dual.**

**Capacity that is fixed in the solve never contributes its capital to the price.** This
always includes capacity that existed before the model's first period. In myopic runs it also
includes everything built in earlier windows: Temoa loads those builds as fixed existing
capacity (`_load_existing_capacity` in `temoa/data_io/hybrid_loader.py`). The remaining
payments on fixed capacity don't depend on any decision in the current solve, so including them
would only add a constant to the objective, and a constant cannot change a dual. Such plants
are paid, if at all, through the gap between the price and their running cost.

**Capacity that is chosen in the same solve can contribute its capital to later periods'
prices.** In a perfect-foresight run, a turbine built in 2025 is a decision variable when the
2030 prices are computed, because the model decided to build it with 2030 in view. The next
section shows how that works.

Earlier builds also affect prices indirectly, through how much capacity exists: an overbuilt
system has prices near running cost, while a tight one has large scarcity rents. That effect
works through the amount of capacity, not its cost.

### 2.4 Perfect foresight in detail: how a 2025 turbine's capital reaches the 2030 price

In the objective, a GW of turbine built in 2025 is charged one yearly payment (capital plus
fixed O&M) for every year from 2025 to the end of the horizon, each discounted to 2020. That
total can be written as a sum of per-period pieces:

```
Cost_2025 = (A + F) × (DF_2025 + DF_2030 + … + DF_2050) = 47.30 × 20.29 ≈ 959 M$ per GW
```

Let ρ_p be the reserve-margin dual in period p, and cc the capacity credit. A linear program
only builds something when its cost exactly equals the value it provides at the optimal duals.
A GW built in 2025 supplies cc GW of reserve in every period from 2025 onward, so:

```
Cost_v = cc·ρ_v + cc·ρ_(v+5) + … + cc·ρ_2050    for every vintage v that is built
Cost_v ≥ cc·ρ_v + cc·ρ_(v+5) + … + cc·ρ_2050    for every vintage v that is not built
```

The first line is how the 2025 turbine's capital reaches the 2030 price: ρ_2030 is one of the
terms that must add up to its cost. The equation does not say how big each term is. That is
determined by the alternatives the model had, expressed through the inequalities.

The example model in `scripts/reserve_dual_toy.py` makes this concrete. It has one region and
one peak slice, uses Temoa's discounting, and has the turbine's costs above. It was solved with
the HiGHS solver under three load patterns. The table shows the resulting capacity contribution
to the price in the peak slice, in $/MWh:

| Case | What gets built | 2025 | 2030 | 2035–2050 |
|---|---|---|---|---|
| 1. Peak load grows 1 GW every period | a new turbine every period | 1,245 | 1,245 | 1,245 each |
| 2. Peak steps up in 2025, then stays flat | the 2025 turbine only | 5,914 | 0 | 0 |
| 3. Peak steps up in 2030; no building allowed after 2025 | the 2025 turbine only | 0 | 6,530 | 0 |

In all three cases, the reserve duals over the turbine's years of service add up exactly to
its cost (959.43 M$/GW).

**Case 1 is the typical situation.** Because the model builds in both 2025 and 2030, both
conditions hold with equality. Subtracting one from the other shows that the 2025 dual carries
exactly one period's yearly payments, and so does the 2030 dual. Those 2030 payments are the
2025 turbine's payments for 2030–2034, but they are also exactly what a turbine built in 2030
would cost. Since the two numbers are identical, it is not meaningful to ask whose capital is
in the 2030 price. The price is the avoidable cost of one more GW of reserve in 2030: one more
period of yearly payments.

**Case 3 shows the 2030 price carrying all of the 2025 turbine's capital.** The turbine is
needed only in 2030, but the model is not allowed to build then. It must build in 2025 and
carry an idle plant for five years, and the whole 959 M$/GW, including the 2025–2029
payments, lands in the 2030 price, roughly five times case 1. In a real model this happens
only when building later is blocked or more expensive: new-capacity or growth limits, a cost
that rises over time, or the technology no longer being available. That other constraint would
also have its own nonzero dual.

**Case 2 shows that the split can be arbitrary.** The reserve constraint binds in every
period against the same turbine, so many different splits of its cost across periods are
equally valid. Case 1's even split of one yearly payment per period is one of them. The solver
happened to put the whole cost on 2025; another solver, or a slightly different data set, could
put it on 2030 instead. The total payback is fixed, but individual period prices are not. If
period prices jump around with no corresponding change in costs or load, this is the likely
cause.

### 2.5 Myopic runs

In a myopic run, Temoa solves the horizon as a series of shorter windows, each blind to the
periods after it. `temoa_power` is typically run with one-period windows (`view_depth = 1`,
`step_size = 1`). Capacity built in earlier windows enters later windows as fixed existing
capacity, so **in myopic mode the capital cost of earlier builds never enters a later period's
price.** With one-period windows, each period's price includes only running costs plus the
yearly capital and fixed O&M of capacity built in that period.

Applied to the three cases above:

- **Case 1:** the 2030 price is still about 1,245 $/MWh, because building a new turbine in
  2030 is the marginal option.
- **Case 2:** the 2030 price is zero, with no ambiguity, because no new capacity is needed.
- **Case 3:** the 2025 window has no reason to build, because it cannot see the 2030 peak. With
  2030 building ruled out, the model would have to meet the 2030 peak another way, or could not
  meet it at all.

Two consequences follow. First, **nothing ensures that earlier investments recover their
capital.** If a later window brings a tighter carbon cap or a cheaper technology, earlier
plants can be left stranded, and prices need not cover their remaining payments. This reflects
the myopic planner's limited foresight; it is not an error. Second, **window boundaries can
shift prices.** New investments are still priced consistently, because a plant built in a
window is charged a full yearly payment for each year it operates in that window. But
constraints that span several periods are cut off at the window edge, such as multi-period
emission budgets, growth limits, or storage carried between periods. That can affect duals,
especially in the last period of each window.

### 2.6 A reporting gap in myopic runs

Reviewing the myopic code turned up a separate issue: **some capital costs are missing from the
cost outputs of myopic runs.** This affects reported totals, not the model's decisions or its
duals.

In each window, Temoa charges a new plant only for the loan payments that fall inside that
window. Later windows charge investment only for their own new builds. As a result, the
payments due after the building window ends are never charged anywhere, even when the plant
keeps operating. The table that records costs (`output_cost`, both the discounted and
undiscounted investment columns) uses the same cut-off. So does the myopic total system cost,
which is simply the sum of that table.

This was measured on the Utopia database by comparing a myopic run (one-period windows) with a
perfect-foresight run. The investment cost recorded per unit of new capacity was:

| Vintage | Myopic as a share of perfect foresight | Why |
|---|---|---|
| 1990 | 33% | 10 of 30 in-horizon years charged |
| 2000 | 50% (40-yr plants), 67% (15-yr plants) | 10 of 20, or 10 of 15, years charged |
| 2010 (last window) | 100% | both runs end at the same year |

Fixed O&M for plants carried into later windows is charged in every period, and variable and
emission costs are unaffected.

For `temoa_power` with five-year windows, a rough estimate: a 30-year plant built in 2020
would have only about 21% of its discounted capital recorded, a 2045 plant about 52%, and a
2050 plant all of it. Reported total system costs will be understated accordingly.

The model's decisions are unaffected, because within each window the cost charged matches the
years the plant operates there, and in later windows the earlier capital is correctly treated
as sunk. The duals are unaffected for the reasons in §2.3. The practical consequence is that
**prices should not be compared with `output_cost` capital** to judge whether plants recover
their costs; for that, capital would need to be rebuilt over the full horizon from the built
capacity.

---

## 3. How the script turns duals into prices

`scripts/electricity_prices.py` reads a solved Temoa database and produces estimated marginal
prices for electricity. For each slice dual on the chosen commodity (`ELC` by default):

```
price ($/MWh) = dual / DF_p × (dollars per cost unit) / (MWh per commodity unit)
```

**Undoing the discounting.** The script reads the discount rate and periods from the database
and rebuilds DF_p exactly as Temoa's objective does (§1.6). Dividing by it turns each dual into
the undiscounted cost of one more unit in one year of the period. That is the quantity that
behaves like a price.

**Converting units.** Units are read from the database. For `temoa_power`, millions of dollars
per PJ become dollars per MWh by multiplying by 3.6, since one PJ is 277,778 MWh. If the units
aren't recognized, the script stops and asks for the conversion explicitly.

**Checking the sign.** No sign flip is applied by default (§1.4). As a safeguard, the script
warns if most nonzero balance duals in the run are negative, which would suggest a solver with
the opposite convention. A `--flip-sign` option is available for that case.

**Combining myopic windows.** In myopic runs, each window's duals are saved separately, and
the dual table is never cleared between windows. It therefore also contains the look-ahead
results of earlier windows for periods that were later re-solved. For each period, the script
uses the duals from the latest window that starts at or before that period, which is the
solution Temoa kept in its other output tables. The per-slice output records which window each
price came from.

**Averaging.** A per-slice price alone doesn't summarize a period, so the script reports two
averages for each region and period:

- a **load-weighted average**, weighting each slice by the electricity drawn from the grid node
  (storage charging and exports excluded);
- a **time-weighted average**, weighting each slice by its share of the year.

**Outputs.**

- A per-slice CSV: raw dual, discount factor, price, load, slice length, and source window.
- An annual CSV, by region and period: both averages, minimum, median and maximum prices, total
  load, and counts of negative, zero and very high (default above 500 $/MWh) slice prices.
- A printed table of load-weighted prices by region and period, plus diagnostics flagging
  negative prices, zero prices in slices with load, price spikes, and periods where the two
  averages differ sharply.

**Safety.** The script opens the database read-only and changes nothing in it.

**Validation.** On copies of the Utopia tutorial database:

- a fuel with a known 2.0 M$/PJ import cost was priced at exactly 7.20 $/MWh in every period,
  in both perfect-foresight and myopic runs (confirming the discount factor, units, sign and
  myopic base year);
- in a myopic run with overlapping windows, the script correctly ignored an earlier window's
  look-ahead dual for a period that was later re-solved;
- perfect-foresight and myopic electricity prices differed only by amounts explained by their
  different investment decisions.

**Usage.** Solve the model with `save_duals = true` and a solver that returns duals. Gurobi
works; the `appsi_highs` interface does not return duals, and Temoa's Monte Carlo mode disables
them. Then run:

```
uv run python scripts/electricity_prices.py temoa_power.sqlite --commodity ELC ELCP --out-dir price_out
```

---

## 4. Caveats when reading the prices

**These are marginal values.** A dual is the slope of the cost curve at the optimum, valid for
small changes. One PJ in a 57-hour slice is roughly 4.9 GW of extra load, enough to change
which plant or constraint is marginal. Treat "the cost of one more PJ" as the cost of the first
small amount, extended in a straight line. Where the solution is degenerate (several equally
good solutions), adding load and removing load can have different marginal costs, and the
solver reports one of them.

**A slice is a representative hour, not a calendar hour.** Each price applies to one
representative hour that stands for about 57 real hours per year in `S1` and 34 in `S2`. Because
capacity costs are concentrated on the few hours of binding slices, peak-slice prices above
1,000 $/MWh are expected when new capacity is needed.

**Individual peak prices can be arbitrary.** When several slices, or several periods, tie at
the binding peak, how the capacity cost is split among them is not unique (case 2 in §2.4). The
symptoms are one very expensive slice next to cheap neighbours, or prices that jump between
periods without any change in costs or load. In the Utopia test, the winter day and night
slices split into +124 and −49 $/MWh in one period, and +160 and −103 in another, while
all other slices were around 19–26 $/MWh. That pattern reflects a constraint linking the two
slices, such as storage or a fixed day/night ratio, not a real negative price. **Load-weighted
period averages are robust to this; individual peak-slice prices are only indicative.**

**Negative prices** can be real. Because the balance is an equality, surplus production with
nowhere to go can have a negative value: for example must-run output, renewable mandates, or
fixed output ratios. They can also arise from the degeneracy above. The script counts them;
check whether they line up with a plausible cause.

**The price depends on where it is measured.** `ELC` is measured after grid losses. The busbar
price at `ELCP` is roughly 0.953 × the `ELC` price. Prices delivered to the residential,
commercial and transport sectors add their delivery costs. The script can price several nodes
at once.

**Policy costs are included.** If a CO₂ cap or a renewable mandate binds, its cost per MWh is
in the price. That is correct for marginal cost under the policy. Separating out the physical
resource cost requires breaking the price into parts using those constraints' duals (§2.1).

**This is a planning model's marginal cost, not a market price.** It assumes investment
responds optimally within each solve. Capacity costs appear as very high prices concentrated in
binding slices, rather than as a separate capacity payment. In perfect foresight, prices can
include the capital of plants built in earlier periods (§2.4); in myopic runs they never do
(§2.5).

**Myopic prices reflect limited foresight.** They are correct for each window as solved, given
the fleet it inherited. Differences from perfect-foresight prices come from what the planner
cannot see and from window-boundary effects, not from the missing costs in the reports (§2.6).
Nothing guarantees that earlier investments recover their capital.

**Solver settings affect precision.** Temoa sets Gurobi to use the barrier algorithm, stop
without the final "crossover" step to an exact corner solution, and accept a loose convergence
tolerance (`temoa/_internal/run_actions.py`, lines 219–222). The duals are therefore only
approximately optimal: expect small nonzero prices where zero would be exact, and slice prices
that are off by a few percent, especially in a model as large as `temoa_power`. Without the
final step, the solver also tends to spread a tied capacity cost evenly across slices and
periods instead of placing it in one. That makes hourly profiles look smoother, but the split
remains a numerical choice, not something the model determines. **For results that matter,
re-solve once with a tight tolerance and crossover enabled, and compare.** If slice prices move
a lot, report period averages rather than hourly shapes.

**How the reserve margin works matters.** Temoa's reserve requirement scales with the output of
reserve-eligible plants in each slice, not with load directly. The 1.5× capacity factor in §2.2
applies when the extra supply comes from a reserve-eligible plant. Temoa's static and dynamic
reserve methods also credit capacity differently, so check which one a run used.

**Reported costs and prices are different questions.** The understated capital in myopic cost
outputs (§2.6) does not affect the prices, but it does affect any comparison between prices and
costs.

---

## 5. Comparing marginal prices with average cost

A natural check on the marginal prices is to compare them with the average cost of
electricity: total cost divided by electricity produced. Doing that correctly requires knowing
exactly what Temoa's cost table reports, and the result is informative whichever way the
comparison comes out.

### 5.1 What the `output_cost` columns measure

Temoa reports costs in `output_cost`, with a discounted and an undiscounted version of each
cost type. The columns do not all cover the same span of time.

**Fixed, variable and emission costs cover the whole period.** Temoa calculates each as one
representative year's cost and multiplies it by the period discount factor DF_p (§1.6). So
`d_fixed`, `d_var` and `d_emiss` are the discounted totals for all years of the period. The
undiscounted columns `fixed`, `var` and `emiss` are one year's cost multiplied by the period
length. This was confirmed on the Utopia test database, which has 10-year periods: the
recorded variable cost was exactly 10 times one year's activity times its variable cost, and
the ratio of discounted to undiscounted cost was 0.7722, which is DF_1990 / 10. Fixed costs gave
the same ratio. In other words, `d_x / DF_p` and `x / LEN_p` both give the cost of a single
representative year.

**Investment cost is a lump sum recorded in the year capacity is built.** `d_invest` appears
under the period equal to the plant's vintage. It is the entire stream of capital payments the
model charges for that capacity, discounted to the base year. That stream covers the plant's
life up to the end of the horizon: 2055 in perfect foresight, or the end of the window in
myopic runs, which is the reporting gap described in §2.6. The undiscounted `invest` column is
the same stream without discounting. A plant built in 2025 therefore shows all of its
2025–2054 payments in its 2025 row, and nothing in later rows.

### 5.2 Computing an average cost that matches the prices

To compare like with like, the average cost has to be on the same basis as the marginal prices
produced by the script: undiscounted dollars for one year of the period, per MWh at the `ELC`
node.

- **Fixed, variable and emission costs:** dividing discounted cost by discounted electricity
  for a single period works, because the discount factor cancels. It is equivalent to
  `(fixed + var + emiss) / LEN_p`, divided by one year's electricity.
- **Investment: do not use `d_invest` as listed.** Because it places decades of capital in the
  build period and none afterwards, it would make average cost spike in build periods and fall
  too low in all others. Instead, add up the yearly capital payment (for example about
  26.8 M$/GW-yr for the gas turbine in §2.2) for every vintage still in service in that
  period. In myopic runs this also avoids the truncated capital reporting.
- **Use the same scope as the price.** The `ELC` price includes fuel valued at its marginal
  cost, grid losses, storage and transmission. The average cost should include upstream fuel
  costs (or value fuel at its own dual), and the costs of the grid, storage and transmission
  technologies.
- **Use the same energy.** Divide by electricity consumed at `ELC`, the same quantity the
  script uses for load-weighting, not by generation at `ELCP`. Generation is larger because of
  grid losses, so dividing by it would understate the cost per MWh delivered.

### 5.3 Should average cost always be lower than the average marginal price?

No. The comparison can go either way, and which way it goes tells you something about the
system.

**The benchmark case.** Linear programs satisfy an exact accounting identity: at the optimum,
total cost equals the sum over all constraints of each constraint's dual multiplied by its
right-hand side. Suppose every plant in use is newly built at a constant cost, and nothing else
binds: no capacity or resource limits, no existing capacity, no policy constraints. Then revenue
at the marginal prices exactly covers cost, and **the load-weighted average marginal price
equals the average cost.** Departures from that benchmark identify which of the following
situations applies.

**When the average marginal price is above average cost.** Marginal prices then pay rents to
something whose cost is missing from, or understated in, `output_cost`:

- **Existing capacity.** Plants built before 2020 have no investment cost in `output_cost`, and
  in myopic runs the capital of earlier windows is only partly recorded. When that capacity is
  scarce, prices still reflect the cost of new capacity.
- **Limited low-cost resources**, such as caps on wind, solar or hydro sites, capacity upper
  bounds, or resource limits. The cheap units earn the difference between the price and their
  cost.
- **Binding CO₂ caps or renewable mandates.** The price includes the constraint's dual times
  the emissions per unit of output. Unless the database also sets an explicit emission price
  (`cost_emission`), that cost appears nowhere in `output_cost`.
- **Upstream rents.** Fuel enters the price at its marginal value, which can be well above its
  average supply cost.

**When average cost is above the average marginal price.** Costs are then being incurred that
the marginal price does not pay for:

- **Excess or forced capacity.** Capacity overbuilt relative to later needs, which is common in
  myopic runs, as well as minimum-build constraints, minimum-activity constraints, or required
  shares.
- **Falling technology costs.** Older plants cost more than today's new build, and today's new
  build is what sets the marginal price.
- **Surplus hours.** Zero or negative prices in slices with surplus electricity pull the average
  price down.
- **Solver imprecision.** Temoa's loose barrier settings make the duals approximate (§4).

### 5.4 What to expect for `temoa_power`

In early periods, the average marginal price will probably be above average cost, because of
existing capacity, resource limits and any binding policy. In later periods, if new builds
dominate and costs are stable, the two should move closer together. In myopic runs, recorded
investment is truncated (§2.6), which biases a measured average cost downward, so the capital
accounting should be rebuilt before drawing conclusions.

When average cost exceeds the marginal price, look for stranded or forced capacity. When the
marginal price is well above average cost, the rents can be traced to the binding constraints
with large duals.

---

## 6. Quick reference

| Item | `temoa_power` |
|---|---|
| Electricity balance constraint | `commodity_balance_constraint[r,p,s,d,ELC]`: equality, one per slice |
| Meaning of a positive dual | marginal cost of serving more load (no sign flip needed) |
| Raw dual units | M$ discounted to 2020, per PJ, in `output_dual_variable` |
| Period discount factor | sum of yearly discount factors over the 5-year period, end-of-year convention, 2% rate, base year 2020 |
| Conversion to a price | `price ($/MWh) = dual ÷ DF_p × 3.6` |
| Time slices | 2 seasons × 96 representative hours; each stands for ≈ 57 h/yr (`S1`) or 34 h/yr (`S2`) |
| Myopic duals | stored per window; the script uses the latest window starting at or before each period |
| Earlier-period capital in prices | possible in perfect foresight; never in myopic runs |
| Myopic cost reports | investment costs cut off at each window's end; prices unaffected |
| `output_cost` time span | fixed, variable and emission costs: whole period; investment: lump sum of in-horizon payments in the vintage row |
| Average cost vs. marginal price | equal only in the benchmark case; the direction of the gap points to rents or forced costs (§5) |

## Appendix: status of the `temoa_power` analysis

At the time of writing, `temoa_power.sqlite` contains model inputs only; it has not yet been
solved with duals saved. The `temoa_power` figures above (time slices, discount factors, gas
turbine costs) are therefore computed from its inputs, and the tested numerical results come
from the Utopia tutorial database. The next step is to solve `temoa_power` in myopic mode with
`save_duals = true` using Gurobi, then run the script as shown in §3.
