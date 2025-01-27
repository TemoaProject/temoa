"""
This file is intended as a QA tool for calculating costs associated with unit-sized purchases
of storage capacity
"""

from temoa.temoa_model.temoa_rules import *

# Written by:  J. F. Hyink
# jeff@westernspark.us
# https://westernspark.us
# Created on:  12/30/23


M = TemoaModel()

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

# make SETS
M.NewCapacityVar_rtv.construct(data=rtv)
M.CapacityVar_rptv.construct(data=rptv)
M.CostInvest_rtv.construct(data=rtv)
M.CostFixed_rptv.construct(data=rptv)
M.LoanLifetimeProcess_rtv.construct(data=rtv)
M.Loan_rtv.construct(data=rtv)
M.LoanRate_rtv.construct(data=rtv)
M.LifetimeProcess_rtv.construct(data=rtv)
M.regionalIndices.construct(data=['A'])
M.MyopicBaseyear.construct(data={None: 0})
M.ModelProcessLife_rptv.construct(data=rptv)


# make PARAMS
M.time_optimize.construct([2020, 2025])
M.time_future.construct([2020, 2025, 2030])  # needs to go 1 period beyond optimize horizon
M.PeriodLength.construct()
M.tech_all.construct(data=['battery'])
M.regions.construct(data=['A'])
M.CostInvest.construct(data={rtv: 1300})  # US_9R_8D
M.CostFixed.construct(data={rptv: 20})  # US_9R_8D
M.LoanLifetimeProcess.construct(data={rtv: 10})
M.LoanRate.construct(data={rtv: 0.05})
M.LoanAnnualize.construct()
M.LifetimeTech.construct(data={('A', 'battery'): 20})
M.LifetimeProcess.construct(data={rtv: 40})
M.ModelProcessLife.construct(data={rptv: 20})
M.GlobalDiscountRate.construct(data={None: 0.05})

# make/fix VARS
M.V_NewCapacity.construct()
M.V_NewCapacity[rtv].set_value(1)

M.V_Capacity.construct()
M.V_Capacity[rptv].set_value(1)

# run the total cost rule on our "model":
tot_cost_expr = TotalCost_rule(M)
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
M.time_season.construct(data=['winter', 'summer'])
tod_slices = 2
M.time_of_day.construct(data=range(1, tod_slices + 1))
M.tech_storage.construct(data=['battery'])
M.ProcessLifeFrac_rptv.construct(data=[rptv])
M.StorageLevel_rpsdtv.construct(
    data=[
        ('A', 2020, 'winter', 1, 'battery', 2020),
    ]
)
M.StorageConstraints_rpsdtv.construct(
    data=[
        ('A', 2020, 'winter', 1, 'battery', 2020),
    ]
)

# More PARAMS
M.CapacityToActivity.construct(data={('A', 'battery'): 31.536})
M.StorageDuration.construct(data={('A', 'battery'): 4})
seasonal_fractions = {'winter': 0.4, 'summer': 0.6}
M.SegFrac.construct(
    data={(s, d): seasonal_fractions[s] / tod_slices for d in M.time_of_day for s in M.time_season}
)
# QA the total
print(f'quality check.  Total of all SegFrac: {sum(M.SegFrac.values()):0.3f}')
M.ProcessLifeFrac.construct(data={('A', 2020, 'battery', 2020): 1.0})

# More VARS
M.V_StorageLevel.construct()
M.SegFracPerSeason.construct()

upper_limit = StorageEnergyUpperBound_Constraint(M, 'A', 2020, 'winter', 1, 'battery', 2020)
print('The storage level constraint for the single period in the "super day":\n', upper_limit)

# cross-check the multiplier...
mulitplier = storage_dur * M.SegFracPerSeason['winter'] * 365 * c2a * c
print(f'The multiplier for the storage should be: {mulitplier}')

M.StorageEnergyUpperBoundConstraint.construct()
