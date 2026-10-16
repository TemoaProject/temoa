-- Unit commitment startup accounting when a season stands for more than one day.
-- The period is 8 days (days_per_period = 8 in config_uc_starts.toml):
--   season a stands for 2 days, season b for 6 days.
-- One generator built from 1 MW units serves a demand that exists only in the 'day' slice.
--   a-days need 2 units online during the day, b-days need 1.
--   With min_output_fraction 0.6 and no night demand every unit must be offline at night,
--   so each represented day starts 2 MW (a) or 1 MW (b): 2*2 + 1*6 = 10 MW started per period-year.
REPLACE INTO metadata VALUES('DB_MAJOR',4,'DB major version number');
REPLACE INTO metadata VALUES('DB_MINOR',0,'DB minor version number');
REPLACE INTO metadata_real VALUES('global_discount_rate',0.05000000000000000277,'Discount Rate for future costs');
REPLACE INTO metadata_real VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in LoanRate table');
REPLACE INTO sector_label VALUES('energy',NULL);
REPLACE INTO region VALUES('region',NULL);
REPLACE INTO commodity VALUES('ethos','s',NULL,NULL);
REPLACE INTO commodity VALUES('fuel','p',NULL,NULL);
REPLACE INTO commodity VALUES('elc','d',NULL,NULL);
REPLACE INTO commodity VALUES('co2','e',NULL,NULL);
REPLACE INTO technology VALUES('imp_fuel','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
REPLACE INTO technology VALUES('gen','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
REPLACE INTO time_period VALUES(1,2020,'f');
REPLACE INTO time_period VALUES(2,2025,'f');
REPLACE INTO time_of_day VALUES(1,'day',12.0,NULL);
REPLACE INTO time_of_day VALUES(2,'night',12.0,NULL);
REPLACE INTO time_season VALUES(1,'a',0.25,'2 of 8 days');
REPLACE INTO time_season VALUES(2,'b',0.75,'6 of 8 days');
REPLACE INTO efficiency VALUES('region','ethos','imp_fuel',2020,'fuel',1.0,NULL,NULL);
REPLACE INTO efficiency VALUES('region','fuel','gen',2020,'elc',1.0,NULL,NULL);
REPLACE INTO capacity_to_activity VALUES('region','imp_fuel',192.0,NULL,'24 h x 8 days');
REPLACE INTO capacity_to_activity VALUES('region','gen',192.0,NULL,'24 h x 8 days');
REPLACE INTO cost_invest VALUES('region','gen',2020,10.0,NULL,NULL);
REPLACE INTO cost_variable VALUES('region',2020,'imp_fuel',2020,1.0,NULL,NULL);
REPLACE INTO cost_emission VALUES('region',2020,'co2',2.0,NULL,NULL);
REPLACE INTO demand VALUES('region',2020,'elc',120.0,NULL,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2020,'a','day','elc',0.4,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2020,'a','night','elc',0.0,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2020,'b','day','elc',0.6,NULL);
REPLACE INTO demand_specific_distribution VALUES('region',2020,'b','night','elc',0.0,NULL);
REPLACE INTO unit_commitment VALUES('region','gen',1.0,0.6,1.0,0,0,0,NULL,NULL);
REPLACE INTO unit_commitment_startup_cost VALUES('region','gen',3.0,NULL,NULL);
REPLACE INTO unit_commitment_startup_emissions VALUES('region','co2','gen',5.0,NULL,NULL);
REPLACE INTO unit_commitment_startup_input VALUES('region','fuel','gen',7.0,NULL,NULL);
