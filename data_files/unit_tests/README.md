# Unit test databases

This unit test directory contains several simple test databases that 
can be used to test specific Temoa constraints in isolation. A brief 
description of these databases follow.

1. three_vehicle_test.sql

This data file serves as a unit test on several of the constraints
within Temoa. 

The database includes a refinery (S_OILREF) that consumes crude oil and
produces gasoline (GSL) and diesel (DSL), which are in turn consumed by
vehicle technologies T_GSL and T_DSL, respectively. The database also
includes wind generation (WIND) that produces electricity (ELC) that is
consumed by electric vehicles (T_EV). The three vehicle technologies all
meet a single end-use demand for vehicle miles traveled (VMT).

S_OILREF includes a TechOutputSplit constraint that requires fixed shares
of diesel and gasoline. Combined with a MinCapacity constraint on T_GSL,
the database tests the V_Flex variable in the CommodityBalance_Constraint,
which allows for the overproduction of a given commodity, in this case
DSL_F, which is produced by a dummy process T_DUM that sits between
S_OILREF and T_DSL. The dummy process is needed, since we need to define
a technology whose output can exceed the model's internal demands. Thus
T_DUM is placed in the tech_flex set.

In addition, WIND has a 100% capacity factor during the day slice, and
50% capacity factor during the night slice. It belongs to the curtailment
set. Capacity must be sufficient to meet demand, and this excess ELC
is produced during the day.

Finally, emissions are associated with S_OILREF and WIND, and we check
to make sure that emissions from curtailed wind and excess DSL are
included.

Thus this very simple dataset tests the following constraints: 
Capacity_Constraint, Demand_Constraint, DemandActivity_Constraint,
CommodityBalance_Constraint, EmissionsLimit_Constraint,
MinActivity_Constraint,TechOutputSplit_Constraint

2. linkedtech_test.sql

This data file serves as a unit test for the LinkedTechs constraint 
within Temoa. 

This database inludes a natural gas combined cycle power plant with 
carbon capture (E_NGCC_CCS) that produces electricity and generates CO2 emissions.
The CO2 emissions commodity can be turned into a physical commodity 
that can be sequestered in the ground. The database includes a dummy 
sink for the physical CO2 emissions commodity and an alternate dummy
process that can also generate the physical CO2 emissions commodity
that can meet the sequestration demand. 

The physical CO2 emissions commodity is generated via a dummy process
(E_NGCC_CCS_emissions) that is linked to the E_NGCC_CCS technology
via the LinkedTechs table. In this way, the amount of physical CO2 emissions 
commodity produced by the E_NGCC_CCS_emissions is equal to the generated CO2 
emissions from the E_NGCC_CCS technology.





