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
model.PeriodLength.construct()
model.tech_all.construct(data=['battery'])
model.regions.construct(data=['A'])
model.regionalIndices.construct(data=['A'])

# make SETS
model.NewCapacityVar_rtv.construct(data=rtv)
model.CapacityVar_rptv.construct(data=rptv)
model.CostInvest_rtv.construct(data=rtv)
model.CostFixed_rptv.construct(data=rptv)
model.LoanLifetimeProcess_rtv.construct(data=rtv)
# M.Loan_rtv.construct(data=rtv)
# M.LoanRate_rtv.construct(data=rtv)
model.LifetimeProcess_rtv.construct(data=rtv)
model.MyopicDiscountingYear.construct(data={None: 0})
# M.ModelProcessLife_rptv.construct(data=rptv)


# make PARAMS
model.CostInvest.construct(data={rtv: 1300})  # US_9R_8D
model.CostFixed.construct(data={rptv: 20})  # US_9R_8D
model.LoanLifetimeProcess.construct(data={rtv: 10})
model.LoanRate.construct(data={rtv: 0.05})
model.LoanAnnualize.construct()
model.LifetimeTech.construct(data={('A', 'battery'): 20})
model.LifetimeProcess.construct(data={rtv: 40})
# M.ModelProcessLife.construct(data={rptv: 20})
model.GlobalDiscountRate.construct(data={None: 0.05})
model.isSurvivalCurveProcess[rtv] = False

# make/fix VARS
model.V_NewCapacity.construct()
model.V_NewCapacity[rtv].set_value(1)

model.V_Capacity.construct()
model.V_Capacity[rptv].set_value(1)

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
model.time_season.construct(['winter', 'summer'])
model.TimeSeason.construct(data={2020: {'winter', 'summer'}, 2025: {'winter', 'summer'}})
model.DaysPerPeriod.construct(data={None: 365})
tod_slices = 2
model.time_of_day.construct(data=range(1, tod_slices + 1))
model.tech_storage.construct(data=['battery'])
model.ProcessLifeFrac_rptv.construct(data=[rptv])
model.StorageLevel_rpsdtv.construct(
    data=[
        ('A', 2020, 'winter', 1, 'battery', 2020),
    ]
)
model.StorageConstraints_rpsdtv.construct(
    data=[
        ('A', 2020, 'winter', 1, 'battery', 2020),
    ]
)

# More PARAMS
model.CapacityToActivity.construct(data={('A', 'battery'): 31.536})
model.StorageDuration.construct(data={('A', 'battery'): 4})
seasonal_fractions = {'winter': 0.4, 'summer': 0.6}
model.SegFrac.construct(
    data={
        (p, s, d): seasonal_fractions[s] / tod_slices
        for d in model.time_of_day
        for p in model.time_optimize
        for s in model.TimeSeason[p]
    }
)
# QA the total
print(f'quality check.  Total of all SegFrac: {sum(model.SegFrac.values()):0.3f}')
model.ProcessLifeFrac.construct(data={('A', 2020, 'battery', 2020): 1.0})

# More VARS
model.V_StorageLevel.construct()
model.SegFracPerSeason.construct()

model.isSeasonalStorage['battery'] = False
upper_limit = storage_energy_upper_bound_constraint(model, 'A', 2020, 'winter', 1, 'battery', 2020)
print('The storage level constraint for the single period in the "super day":\n', upper_limit)

# cross-check the multiplier...
mulitplier = storage_dur * model.SegFracPerSeason[2020, 'winter'] * model.DaysPerPeriod * c2a * c
print(f'The multiplier for the storage should be: {mulitplier}')

model.StorageEnergyUpperBoundConstraint.construct()
