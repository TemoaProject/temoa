-- Unit commitment startup costs in a myopic run (config_uc_myopic_discount.toml).
-- Two optimized periods, 2030 and 2040, solved as one myopic window each; 2050 ends the horizon.
-- One generator built from 1 MW units serves a demand that exists only in the 'day' slice.
--   It delivers through grid, so its own flow is not fixed as the only supply of a demand.
--   Demand needs 2 units online during the day. With min_output_fraction 0.5 and no night
--   demand every unit must be offline at night, so both units start every day.
-- Starts carry a startup cost and startup emissions with an emission cost in both periods.
-- gen also has a variable cost in both periods, the core cost the startup costs are compared with.
REPLACE INTO metadata VALUES('DB_MAJOR',4,'DB major version number');
REPLACE INTO metadata VALUES('DB_MINOR',0,'DB minor version number');
REPLACE INTO metadata_real VALUES('global_discount_rate',0.02,'Discount Rate for future costs');
REPLACE INTO metadata_real VALUES('default_loan_rate',0.02,'Default Loan Rate if not specified in LoanRate table');
REPLACE INTO sector_label VALUES('energy',NULL);
REPLACE INTO region VALUES('region',NULL);
REPLACE INTO commodity VALUES('ethos','s',NULL,NULL);
REPLACE INTO commodity VALUES('power','p',NULL,NULL);
REPLACE INTO commodity VALUES('elc','d',NULL,NULL);
REPLACE INTO commodity VALUES('co2','e',NULL,NULL);
REPLACE INTO technology VALUES('gen','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
REPLACE INTO technology VALUES('grid','p','energy',NULL,NULL,1,0,0,0,0,0,0,0,NULL);
REPLACE INTO time_period VALUES(1,2030,'f');
REPLACE INTO time_period VALUES(2,2040,'f');
REPLACE INTO time_period VALUES(3,2050,'f');
REPLACE INTO time_of_day VALUES(1,'day',12.0,NULL);
REPLACE INTO time_of_day VALUES(2,'night',12.0,NULL);
REPLACE INTO time_season VALUES(1,'s',1.0,NULL);
REPLACE INTO efficiency VALUES('region','ethos','gen',2030,'power',1.0,NULL,NULL);
REPLACE INTO efficiency VALUES('region','power','grid',2030,'elc',1.0,NULL,NULL);
REPLACE INTO capacity_to_activity VALUES('region','gen',8760.0,NULL,NULL);
REPLACE INTO cost_invest VALUES('region','gen',2030,10.0,NULL,NULL);
REPLACE INTO cost_variable VALUES('region',2030,'gen',2030,1.0,NULL,NULL);
REPLACE INTO cost_variable VALUES('region',2040,'gen',2030,1.0,NULL,NULL);
REPLACE INTO cost_emission VALUES('region',2030,'co2',2.0,NULL,NULL);
REPLACE INTO cost_emission VALUES('region',2040,'co2',2.0,NULL,NULL);
REPLACE INTO demand VALUES('region',2030,'elc',8760.0,NULL,NULL);
REPLACE INTO demand VALUES('region',2040,'elc',8760.0,NULL,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2030,'s','day','elc',1.0,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2030,'s','night','elc',0.0,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2040,'s','day','elc',1.0,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2040,'s','night','elc',0.0,NULL);
REPLACE INTO unit_commitment VALUES('region','gen',1.0,0.5,1.0,0,0,0,NULL,NULL);
REPLACE INTO unit_commitment_startup_cost VALUES('region','gen',3.0,NULL,NULL);
REPLACE INTO unit_commitment_startup_emissions VALUES('region','co2','gen',5.0,NULL,NULL);
