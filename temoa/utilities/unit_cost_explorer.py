"""
This file is intended as a QA tool for calculating costs associated with unit-sized purchases
of storage capacity
"""

from pyomo.environ import value

from temoa.components.costs import total_cost_rule
from temoa.components.storage import storage_energy_upper_bound_constraint
from temoa.core.model import TemoaModel

# Written by:  J. F. Hyink
# jeff@westernspark.us
# https://westernspark.us
# Created on:  12/30/23


model = TemoaModel()

"""
let's fill in what we need to cost 1 item...
The goal here is to cost out 1 unit of storage capacity in 1 battery in the year 2020
in a generic region 'A'.

This script is largely a verification of the true cost of 1 unit of storage because the math to
calculate it is somewhat opaque due to the complexity of the cost function and the numerous
factors that are used in calculation
"""


# indices
rtv = ('A', 'battery', 2020)  # rtv
rptv = ('A', 2020, 'battery', 2020)  # rptv
model.time_future.construct([2020, 2025, 2030])  # needs to go 1 period beyond optimize horizon
model.time_optimize.construct([2020, 2025])
model.period_length.construct()
model.tech_all.construct(data=['battery'])
model.regions.construct(data=['A'])
model.regional_indices.construct(data=['A'])

# make SETS
model.new_capacity_var_rtv.construct(data=rtv)
model.capacity_var_rptv.construct(data=rptv)
model.cost_invest_rtv.construct(data=rtv)
model.cost_fixed_rptv.construct(data=rptv)
model.loan_lifetime_process_rtv.construct(data=rtv)
# M.Loan_rtv.construct(data=rtv)
# M.loan_rate_rtv.construct(data=rtv)
model.lifetime_process_rtv.construct(data=rtv)
model.myopic_discounting_year.construct(data={None: 0})
# M.ModelProcessLife_rptv.construct(data=rptv)


# make PARAMS
model.cost_invest.construct(data={rtv: 1300})  # US_9R_8D
model.cost_fixed.construct(data={rptv: 20})  # US_9R_8D
model.loan_lifetime_process.construct(data={rtv: 10})
model.loan_rate.construct(data={rtv: 0.05})
model.loan_annualize.construct()
model.lifetime_tech.construct(data={('A', 'battery'): 20})
model.lifetime_process.construct(data={rtv: 40})
# M.ModelProcessLife.construct(data={rptv: 20})
model.global_discount_rate.construct(data={None: 0.05})
model.is_survival_curve_process[rtv] = False

# make/fix VARS
model.v_new_capacity.construct()
model.v_new_capacity[rtv].set_value(1)

model.v_capacity.construct()
model.v_capacity[rptv].set_value(1)

# run the total cost rule on our "model":
tot_cost_expr = total_cost_rule(model)
total_cost = value(tot_cost_expr)
print()
print(f'Total cost for building 1 capacity unit of storage:  ${total_cost:0.2f} [$M]')
print('The total cost expression:')
print(tot_cost_expr)

# how much storage achieved for 1 unit of capacity?
storage_cap = 1  # unit
storage_dur = 4  # hr
c2a = 31.536  # PJ/GW-yr
c = 1 / 8760  # yr/hr
storage = storage_cap * storage_dur * c2a * c
PJ_to_kwh = 1 / 3600000 * 1e15
print()
print(f'storage built: {storage:0.4f} [PJ] / {(storage * PJ_to_kwh):0.2f} [kWh]')

price_per_kwh = total_cost * 1e6 / (storage * PJ_to_kwh)
print(f'price_per_kwh: ${price_per_kwh: 0.2f}\n')

# let's look at the constraint for storage level
print('building storage level constraint...')

# More SETS
model.time_season_all.construct(['winter', 'summer'])
model.time_season.construct(data={2020: {'winter', 'summer'}, 2025: {'winter', 'summer'}})
model.days_per_period.construct(data={None: 365})
tod_slices = 2
model.time_of_day.construct(data=range(1, tod_slices + 1))
model.tech_storage.construct(data=['battery'])
model.process_life_frac_rptv.construct(data=[rptv])
model.storage_level_rpsdtv.construct(
    data=[
        ('A', 2020, 'winter', 1, 'battery', 2020),
    ]
)
model.storage_constraints_rpsdtv.construct(
    data=[
        ('A', 2020, 'winter', 1, 'battery', 2020),
    ]
)

# More PARAMS
model.capacity_to_activity.construct(data={('A', 'battery'): 31.536})
model.storage_duration.construct(data={('A', 'battery'): 4})
seasonal_fractions = {'winter': 0.4, 'summer': 0.6}
model.segment_fraction.construct(
    data={
        (p, s, d): seasonal_fractions[s] / tod_slices
        for d in model.time_of_day
        for p in model.time_optimize
        for s in model.time_season[p]
    }
)
# QA the total
print(f'quality check.  Total of all segment_fraction: {sum(model.segment_fraction.values()):0.3f}')
model.process_life_frac.construct(data={('A', 2020, 'battery', 2020): 1.0})

# More VARS
model.v_storage_level.construct()
model.segment_fraction_per_season.construct()

model.is_seasonal_storage['battery'] = False
upper_limit = storage_energy_upper_bound_constraint(model, 'A', 2020, 'winter', 1, 'battery', 2020)
print('The storage level constraint for the single period in the "super day":\n', upper_limit)

# cross-check the multiplier...
mulitplier = (
    storage_dur
    * model.segment_fraction_per_season[2020, 'winter']
    * model.days_per_period
    * c2a
    * c
)
print(f'The multiplier for the storage should be: {mulitplier}')

model.storage_energy_upper_bound_constraint.construct()
