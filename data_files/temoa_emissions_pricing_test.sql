BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "CapacityCredit" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"vintage"	integer,
	"cf_tech"	real CHECK("cf_tech" >= 0 AND "cf_tech" <= 1),
	"cf_tech_notes"	text,
	PRIMARY KEY("regions","periods","tech","vintage")
);
CREATE TABLE IF NOT EXISTS "CapacityFactorProcess" (
	"regions"	text,
	"season_name"	text,
	"time_of_day_name"	text,
	"tech"	text,
	"vintage"	integer,
	"cf_process"	real CHECK("cf_process" >= 0 AND "cf_process" <= 1),
	"cf_process_notes"	text,
	PRIMARY KEY("regions","season_name","time_of_day_name","tech","vintage"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day")
);
CREATE TABLE IF NOT EXISTS "CapacityFactorTech" (
	"regions"	text,
	"season_name"	text,
	"time_of_day_name"	text,
	"tech"	text,
	"cf_tech"	real CHECK("cf_tech" >= 0 AND "cf_tech" <= 1),
	"cf_tech_notes"	text,
	PRIMARY KEY("regions","season_name","time_of_day_name","tech"),
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day")
);
CREATE TABLE IF NOT EXISTS "CapacityToActivity" (
	"regions"	text,
	"tech"	text,
	"c2a"	real,
	"c2a_notes"	TEXT,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "CostEmissions" (
	"regions"	text NOT NULL,
	"periods"	integer NOT NULL,
	"emis_comm"	text NOT NULL,
	"emis_penalty"	real,
	"emis_penalty_units"	text,
	"emis_penalty_notes"	text,
	PRIMARY KEY("regions","periods","emis_comm"),
	FOREIGN KEY("regions") REFERENCES "regions"("regions"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("emis_comm") REFERENCES "commodities"("comm_name")
);
CREATE TABLE IF NOT EXISTS "CostFixed" (
	"regions"	text NOT NULL,
	"periods"	integer NOT NULL,
	"tech"	text NOT NULL,
	"vintage"	integer NOT NULL,
	"cost_fixed"	real,
	"cost_fixed_units"	text,
	"cost_fixed_notes"	text,
	PRIMARY KEY("regions","periods","tech","vintage"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "CostInvest" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"cost_invest"	real,
	"cost_invest_units"	text,
	"cost_invest_notes"	text,
	PRIMARY KEY("regions","tech","vintage"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "CostVariable" (
	"regions"	text NOT NULL,
	"periods"	integer NOT NULL,
	"tech"	text NOT NULL,
	"vintage"	integer NOT NULL,
	"cost_variable"	real,
	"cost_variable_units"	text,
	"cost_variable_notes"	text,
	PRIMARY KEY("regions","periods","tech","vintage"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "Demand" (
	"regions"	text,
	"periods"	integer,
	"demand_comm"	text,
	"demand"	real,
	"demand_units"	text,
	"demand_notes"	text,
	PRIMARY KEY("regions","periods","demand_comm"),
	FOREIGN KEY("demand_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "DemandSpecificDistribution" (
	"regions"	text,
	"season_name"	text,
	"time_of_day_name"	text,
	"demand_name"	text,
	"dds"	real CHECK("dds" >= 0 AND "dds" <= 1),
	"dds_notes"	text,
	PRIMARY KEY("regions","season_name","time_of_day_name","demand_name"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("demand_name") REFERENCES "commodities"("comm_name")
);
CREATE TABLE IF NOT EXISTS "DiscountRate" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"tech_rate"	real,
	"tech_rate_notes"	text,
	PRIMARY KEY("regions","tech","vintage"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "Efficiency" (
	"regions"	text,
	"input_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"output_comm"	text,
	"efficiency"	real CHECK("efficiency" > 0),
	"eff_notes"	text,
	PRIMARY KEY("regions","input_comm","tech","vintage","output_comm"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name")
);
CREATE TABLE IF NOT EXISTS "EmissionActivity" (
	"regions"	text,
	"emis_comm"	text,
	"input_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"output_comm"	text,
	"emis_act"	real,
	"emis_act_units"	text,
	"emis_act_notes"	text,
	PRIMARY KEY("regions","emis_comm","input_comm","tech","vintage","output_comm"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("emis_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "EmissionLimit" (
	"regions"	text,
	"periods"	integer,
	"emis_comm"	text,
	"emis_limit"	real,
	"emis_limit_units"	text,
	"emis_limit_notes"	text,
	PRIMARY KEY("regions","periods","emis_comm"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("emis_comm") REFERENCES "commodities"("comm_name")
);
CREATE TABLE IF NOT EXISTS "ExistingCapacity" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"exist_cap"	real,
	"exist_cap_units"	text,
	"exist_cap_notes"	text,
	PRIMARY KEY("regions","tech","vintage"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "GlobalDiscountRate" (
	"rate"	real
);
CREATE TABLE IF NOT EXISTS "GrowthRateMax" (
	"regions"	text,
	"tech"	text,
	"growthrate_max"	real,
	"growthrate_max_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "GrowthRateSeed" (
	"regions"	text,
	"tech"	text,
	"growthrate_seed"	real,
	"growthrate_seed_units"	text,
	"growthrate_seed_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "LifetimeLoanTech" (
	"regions"	text,
	"tech"	text,
	"loan"	real,
	"loan_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "LifetimeProcess" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"life_process"	real,
	"life_process_notes"	text,
	PRIMARY KEY("regions","tech","vintage"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "LifetimeTech" (
	"regions"	text,
	"tech"	text,
	"life"	real,
	"life_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "MaxActivity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"maxact"	real,
	"maxact_units"	text,
	"maxact_notes"	text,
	PRIMARY KEY("regions","periods","tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "MaxCapacity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"maxcap"	real,
	"maxcap_units"	text,
	"maxcap_notes"	text,
	PRIMARY KEY("regions","periods","tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "MaxResource" (
	"regions"	text,
	"tech"	text,
	"maxres"	real,
	"maxres_units"	text,
	"maxres_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
);
CREATE TABLE IF NOT EXISTS "MinActivity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"minact"	real,
	"minact_units"	text,
	"minact_notes"	text,
	PRIMARY KEY("regions","periods","tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "MinCapacity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"mincap"	real,
	"mincap_units"	text,
	"mincap_notes"	text,
	PRIMARY KEY("regions","periods","tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "MinGenGroupTarget" (
	"regions"	text,
	"periods"	integer,
	"group_name"	text,
	"min_act_g"	real,
	"notes"	text,
	PRIMARY KEY("periods","group_name","regions")
);
CREATE TABLE IF NOT EXISTS "MinGenGroupWeight" (
	"regions"	text,
	"tech"	text,
	"group_name"	text,
	"act_fraction"	REAL,
	"tech_desc"	text,
	PRIMARY KEY("tech","group_name","regions")
);
CREATE TABLE IF NOT EXISTS "MyopicBaseyear" (
	"year"	real notes text
);
CREATE TABLE IF NOT EXISTS "Output_CapacityByPeriodAndTech" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"t_periods"	integer,
	"tech"	text,
	"capacity"	real,
	PRIMARY KEY("regions","scenario","t_periods","tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "Output_Costs" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"output_name"	text,
	"tech"	text,
	"vintage"	integer,
	"output_cost"	real,
	PRIMARY KEY("regions","scenario","output_name","tech","vintage"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "Output_Curtailment" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"t_periods"	integer,
	"t_season"	text,
	"t_day"	text,
	"input_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"output_comm"	text,
	"curtailment"	real,
	PRIMARY KEY("regions","scenario","t_periods","t_season","t_day","input_comm","tech","vintage","output_comm"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("t_day") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("t_season") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "Output_Emissions" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"t_periods"	integer,
	"emissions_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"emissions"	real,
	PRIMARY KEY("regions","scenario","t_periods","emissions_comm","tech","vintage"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("emissions_comm") REFERENCES "EmissionActivity"("emis_comm"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE "Output_ImplicitEmissionsPrice" (
	"regions"	text,
	"scenario"	text,
	"t_periods"	integer,
	"emissions_comm"	text,
	"emissions_price"	real,
	PRIMARY KEY("regions","scenario","t_periods","emissions_comm"),
	FOREIGN KEY("emissions_comm") REFERENCES "EmissionActivity"("emis_comm"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "Output_Objective" (
	"scenario"	text,
	"objective_name"	text,
	"total_system_cost"	real
);
CREATE TABLE IF NOT EXISTS "Output_VFlow_In" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"t_periods"	integer,
	"t_season"	text,
	"t_day"	text,
	"input_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"output_comm"	text,
	"vflow_in"	real,
	PRIMARY KEY("regions","scenario","t_periods","t_season","t_day","input_comm","tech","vintage","output_comm"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("t_day") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("t_season") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector")
);
CREATE TABLE IF NOT EXISTS "Output_VFlow_Out" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"t_periods"	integer,
	"t_season"	text,
	"t_day"	text,
	"input_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"output_comm"	text,
	"vflow_out"	real,
	PRIMARY KEY("regions","scenario","t_periods","t_season","t_day","input_comm","tech","vintage","output_comm"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("t_day") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("t_season") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name")
);
CREATE TABLE IF NOT EXISTS "Output_V_Capacity" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"tech"	text,
	"vintage"	integer,
	"capacity"	real,
	PRIMARY KEY("regions","scenario","tech","vintage"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "PlanningReserveMargin" (
	"regions"	text,
	"reserve_margin"	REAL,
	PRIMARY KEY("regions"),
	FOREIGN KEY("regions") REFERENCES "regions"
);
CREATE TABLE IF NOT EXISTS "SegFrac" (
	"season_name"	text,
	"time_of_day_name"	text,
	"segfrac"	real CHECK("segfrac" >= 0 AND "segfrac" <= 1),
	"segfrac_notes"	text,
	PRIMARY KEY("season_name","time_of_day_name"),
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day")
);
CREATE TABLE IF NOT EXISTS "StorageDuration" (
	"regions"	text,
	"tech"	text,
	"duration"	real,
	"duration_notes"	text,
	PRIMARY KEY("regions","tech")
);
CREATE TABLE IF NOT EXISTS "TechInputSplit" (
	"regions"	TEXT,
	"periods"	integer,
	"input_comm"	text,
	"tech"	text,
	"ti_split"	real,
	"ti_split_notes"	text,
	PRIMARY KEY("regions","periods","input_comm","tech"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "TechOutputSplit" (
	"regions"	TEXT,
	"periods"	integer,
	"tech"	text,
	"output_comm"	text,
	"to_split"	real,
	"to_split_notes"	text,
	PRIMARY KEY("regions","periods","tech","output_comm"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods")
);
CREATE TABLE IF NOT EXISTS "commodities" (
	"comm_name"	text,
	"flag"	text,
	"comm_desc"	text,
	PRIMARY KEY("comm_name"),
	FOREIGN KEY("flag") REFERENCES "commodity_labels"("comm_labels")
);
CREATE TABLE IF NOT EXISTS "commodity_labels" (
	"comm_labels"	text,
	"comm_labels_desc"	text,
	PRIMARY KEY("comm_labels")
);
CREATE TABLE IF NOT EXISTS "groups" (
	"group_name"	text,
	"notes"	text,
	PRIMARY KEY("group_name")
);
CREATE TABLE IF NOT EXISTS "regions" (
	"regions"	TEXT,
	"region_note"	TEXT,
	PRIMARY KEY("regions")
);
CREATE TABLE IF NOT EXISTS "sector_labels" (
	"sector"	text,
	PRIMARY KEY("sector")
);
CREATE TABLE IF NOT EXISTS "tech_annual" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "tech_curtailment" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "tech_exchange" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "tech_flex" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE IF NOT EXISTS "tech_reserve" (
	"tech"	text,
	"notes"	text,
	PRIMARY KEY("tech")
);
CREATE TABLE IF NOT EXISTS "technologies" (
	"tech"	text,
	"flag"	text,
	"sector"	text,
	"tech_desc"	text,
	"tech_category"	text,
	PRIMARY KEY("tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("flag") REFERENCES "technology_labels"("tech_labels")
);
CREATE TABLE IF NOT EXISTS "technology_labels" (
	"tech_labels"	text,
	"tech_labels_desc"	text,
	PRIMARY KEY("tech_labels")
);
CREATE TABLE IF NOT EXISTS "time_of_day" (
	"t_day"	text,
	PRIMARY KEY("t_day")
);
CREATE TABLE IF NOT EXISTS "time_period_labels" (
	"t_period_labels"	text,
	"t_period_labels_desc"	text,
	PRIMARY KEY("t_period_labels")
);
CREATE TABLE IF NOT EXISTS "time_periods" (
	"t_periods"	integer,
	"flag"	text,
	PRIMARY KEY("t_periods"),
	FOREIGN KEY("flag") REFERENCES "time_period_labels"("t_period_labels")
);
CREATE TABLE IF NOT EXISTS "time_season" (
	"t_season"	text,
	PRIMARY KEY("t_season")
);
INSERT INTO "CapacityToActivity" VALUES ('R1','S_IMPNG',1.0,'');
INSERT INTO "CapacityToActivity" VALUES ('R1','E_NGCC',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R2','S_IMPNG',1.0,'');
INSERT INTO "CapacityToActivity" VALUES ('R2','E_NGCC',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R1','S_IMPNG_EM',1.0,'');
INSERT INTO "CapacityToActivity" VALUES ('R1','E_NGCC_EM',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R2','S_IMPNG_EM',1.0,'');
INSERT INTO "CapacityToActivity" VALUES ('R2','E_NGCC_EM',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R1-R2','E_TRANS',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R2-R1','E_TRANS',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R1','E_DIST',31.54,'');
INSERT INTO "CapacityToActivity" VALUES ('R2','E_DIST',31.54,'');
INSERT INTO `CostEmissions` VALUES ('R1',2020,'CO2',0.000001,'TK','');
INSERT INTO `CostEmissions` VALUES ('R1',2025,'CO2',0.000001,'TK','');
INSERT INTO `CostEmissions` VALUES ('R2',2020,'CO2',0.000001,'TK','');
INSERT INTO `CostEmissions` VALUES ('R2',2025,'CO2',0.000001,'TK','');
INSERT INTO "CostFixed" VALUES ('R1',2020,'E_NGCC',2020,30.6,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R1',2025,'E_NGCC',2020,9.78,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R1',2025,'E_NGCC',2025,9.78,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R2',2020,'E_NGCC',2020,24.48,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R2',2025,'E_NGCC',2020,7.824,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R2',2025,'E_NGCC',2025,7.824,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R1',2020,'E_NGCC_EM',2020,30.6,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R1',2025,'E_NGCC_EM',2020,9.78,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R1',2025,'E_NGCC_EM',2025,9.78,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R2',2020,'E_NGCC_EM',2020,24.48,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R2',2025,'E_NGCC_EM',2020,7.824,'$M/GWyr','');
INSERT INTO "CostFixed" VALUES ('R2',2025,'E_NGCC_EM',2025,7.824,'$M/GWyr','');
INSERT INTO "CostInvest" VALUES ('R1','E_NGCC',2020,1060.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R1','E_NGCC',2025,1060.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R2','E_NGCC',2020,1060.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R2','E_NGCC',2025,1060.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R1','E_NGCC_EM',2020,1050.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R1','E_NGCC_EM',2025,1050.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R2','E_NGCC_EM',2020,1050.0,'$M/GW','');
INSERT INTO "CostInvest" VALUES ('R2','E_NGCC_EM',2025,1050.0,'$M/GW','');
INSERT INTO "CostVariable" VALUES ('R1',2020,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2025,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2020,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2025,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2025,'E_NGCC',2025,1.7,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2020,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2020,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'E_NGCC',2025,1.36,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2020,'S_IMPNG_EM',2020,4.0,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2025,'S_IMPNG_EM',2020,4.0,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2020,'E_NGCC_EM',2020,1.6,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2025,'E_NGCC_EM',2020,1.6,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2025,'E_NGCC_EM',2025,1.7,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2020,'S_IMPNG_EM',2020,3.2,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'S_IMPNG_EM',2020,3.2,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2020,'E_NGCC_EM',2020,1.28,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'E_NGCC_EM',2020,1.28,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'E_NGCC_EM',2025,1.36,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1-R2',2020,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1-R2',2025,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2-R1',2020,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2-R1',2025,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R1',2020,'E_DIST',2015,0.1,'$M/PJ','');
INSERT INTO "CostVariable" VALUES ('R2',2025,'E_DIST',2015,0.1,'$M/PJ','');
INSERT INTO "Demand" VALUES ('R1',2020,'ELCD',300.0,'','');
INSERT INTO "Demand" VALUES ('R1',2025,'ELCD',330.0,'','');
INSERT INTO "Demand" VALUES ('R2',2020,'ELCD',700.0,'','');
INSERT INTO "Demand" VALUES ('R2',2025,'ELCD',770.0,'','');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','spring','day','ELCD',0.05,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','spring','night','ELCD',0.1,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','summer','day','ELCD',0.0,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','summer','night','ELCD',0.0,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','fall','day','ELCD',0.05,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','fall','night','ELCD',0.1,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','winter','day','ELCD',0.3,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R1','winter','night','ELCD',0.4,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','spring','day','ELCD',0.05,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','spring','night','ELCD',0.1,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','summer','day','ELCD',0.0,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','summer','night','ELCD',0.0,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','fall','day','ELCD',0.05,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','fall','night','ELCD',0.1,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','winter','day','ELCD',0.3,'');
INSERT INTO "DemandSpecificDistribution" VALUES ('R2','winter','night','ELCD',0.4,'');
INSERT INTO "Efficiency" VALUES ('R1','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO "Efficiency" VALUES ('R1','NG','E_NGCC',2020,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R1','NG','E_NGCC',2025,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R2','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO "Efficiency" VALUES ('R2','NG','E_NGCC',2020,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R2','NG','E_NGCC',2025,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R1','ethos','S_IMPNG_EM',2020,'NG_EM',1.0,'');
INSERT INTO "Efficiency" VALUES ('R1','NG_EM','E_NGCC_EM',2020,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R1','NG_EM','E_NGCC_EM',2025,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R2','ethos','S_IMPNG_EM',2020,'NG_EM',1.0,'');
INSERT INTO "Efficiency" VALUES ('R2','NG_EM','E_NGCC_EM',2020,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R2','NG_EM','E_NGCC_EM',2025,'ELC',0.55,'');
INSERT INTO "Efficiency" VALUES ('R1','ELC','E_DIST',2015,'ELCD',1.0,'');
INSERT INTO "Efficiency" VALUES ('R2','ELC','E_DIST',2015,'ELCD',1.0,'');
INSERT INTO "Efficiency" VALUES ('R1-R2','ELC','E_TRANS',2015,'ELC',0.9,'');
INSERT INTO "Efficiency" VALUES ('R2-R1','ELC','E_TRANS',2015,'ELC',0.9,'');
INSERT INTO "EmissionActivity" VALUES ('R1','CO2','ethos','S_IMPNG_EM',2020,'NG_EM',50.3,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "EmissionActivity" VALUES ('R2','CO2','ethos','S_IMPNG_EM',2020,'NG_EM',50.3,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "EmissionLimit" VALUES ('R1',2020,'CO2',26700.0,NULL,NULL);
INSERT INTO "ExistingCapacity" VALUES ('R1','E_DIST',2015,1000.0,'GW','');
INSERT INTO "ExistingCapacity" VALUES ('R2','E_DIST',2015,1000.0,'GW','');
INSERT INTO "ExistingCapacity" VALUES ('R1-R2','E_TRANS',2015,10.0,'GW','');
INSERT INTO "ExistingCapacity" VALUES ('R2-R1','E_TRANS',2015,10.0,'GW','');
INSERT INTO "GlobalDiscountRate" VALUES (0.05);
INSERT INTO "LifetimeTech" VALUES ('R1','S_IMPNG',100.0,'');
INSERT INTO "LifetimeTech" VALUES ('R1','E_NGCC',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R2','S_IMPNG',100.0,'');
INSERT INTO "LifetimeTech" VALUES ('R2','E_NGCC',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R1','S_IMPNG_EM',100.0,'');
INSERT INTO "LifetimeTech" VALUES ('R1','E_NGCC_EM',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R2','S_IMPNG_EM',100.0,'');
INSERT INTO "LifetimeTech" VALUES ('R2','E_NGCC_EM',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R1','E_DIST',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R2','E_DIST',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R1-R2','E_TRANS',30.0,'');
INSERT INTO "LifetimeTech" VALUES ('R2-R1','E_TRANS',30.0,'');
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1','test_run','electric',2020,'E_NGCC_EM',30.1204819277108);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2-R1','test_run','electric',2025,'E_TRANS',10.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1','test_run','electric',2020,'E_DIST',1000.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2','test_run','electric',2025,'E_NGCC_EM',78.4400760938491);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1','test_run','supply',2020,'S_IMPNG_EM',1901.81818181818);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2','test_run','electric',2020,'E_NGCC_EM',71.3379835129994);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2','test_run','supply',2025,'S_IMPNG_EM',4498.18181818182);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1-R2','test_run','electric',2020,'E_TRANS',10.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2-R1','test_run','electric',2020,'E_TRANS',10.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2','test_run','electric',2025,'E_DIST',1000.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2','test_run','electric',2020,'E_DIST',1000.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1','test_run','supply',2025,'S_IMPNG_EM',1901.81818181818);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1','test_run','electric',2025,'E_NGCC_EM',33.1642358909322);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1','test_run','electric',2025,'E_DIST',1000.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R1-R2','test_run','electric',2025,'E_TRANS',10.0);
INSERT INTO "Output_CapacityByPeriodAndTech" VALUES ('R2','test_run','supply',2020,'S_IMPNG_EM',4498.18181818182);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedInvestmentByProcess','E_NGCC_EM',2020,15886.3082944463);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedInvestmentByProcess','E_NGCC_EM',2020,16680.6237091687);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedInvestmentByProcess','E_NGCC_EM',2025,900.100760734564);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedInvestmentByProcess','E_NGCC_EM',2025,740.515123418381);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedInvestmentByProcess','E_NGCC_EM',2020,37625.4670131624);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedInvestmentByProcess','E_NGCC_EM',2020,39506.7403638205);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedInvestmentByProcess','E_NGCC_EM',2025,2100.23510838065);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedInvestmentByProcess','E_NGCC_EM',2025,1727.86862130956);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedFixedCostsByProcess','E_NGCC_EM',2020,6081.32530120482);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedFixedCostsByProcess','E_NGCC_EM',2020,5239.19233386926);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedFixedCostsByProcess','E_NGCC_EM',2025,148.839568801522);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedFixedCostsByProcess','E_NGCC_EM',2025,106.029473857981);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedFixedCostsByProcess','E_NGCC_EM',2020,11522.5110970197);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedFixedCostsByProcess','E_NGCC_EM',2020,9926.89073785754);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedFixedCostsByProcess','E_NGCC_EM',2025,277.833861762841);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedFixedCostsByProcess','E_NGCC_EM',2025,197.921684534899);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','supply','V_UndiscountedVariableCostsByProcess','S_IMPNG_EM',2020,22363.6363636364);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','supply','V_DiscountedVariableCostsByProcess','S_IMPNG_EM',2020,18024.6834565115);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedVariableCostsByProcess','E_NGCC_EM',2020,4824.0);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedVariableCostsByProcess','E_NGCC_EM',2020,3897.04243394009);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedVariableCostsByProcess','E_NGCC_EM',2025,102.0);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedVariableCostsByProcess','E_NGCC_EM',2025,72.6621718982265);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','supply','V_UndiscountedVariableCostsByProcess','S_IMPNG_EM',2020,43200.0);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','supply','V_DiscountedVariableCostsByProcess','S_IMPNG_EM',2020,34825.3953019455);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedVariableCostsByProcess','E_NGCC_EM',2020,9324.8);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedVariableCostsByProcess','E_NGCC_EM',2020,7533.92950364212);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedVariableCostsByProcess','E_NGCC_EM',2025,190.4);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedVariableCostsByProcess','E_NGCC_EM',2025,135.636054210023);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedVariableCostsByProcess','E_DIST',2015,150.0);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedVariableCostsByProcess','E_DIST',2015,136.378515124871);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedVariableCostsByProcess','E_DIST',2015,385.0);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedVariableCostsByProcess','E_DIST',2015,274.264080204091);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_UndiscountedVariableCostsByProcess','E_TRANS',2015,7.5);
INSERT INTO "Output_Costs" VALUES ('R1','test_run','electric','V_DiscountedVariableCostsByProcess','E_TRANS',2015,6.08086625673304);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_UndiscountedVariableCostsByProcess','E_TRANS',2015,0.0);
INSERT INTO "Output_Costs" VALUES ('R2','test_run','electric','V_DiscountedVariableCostsByProcess','E_TRANS',2015,0.0);
INSERT INTO "Output_Emissions" VALUES ('R2','test_run','supply',2025,'CO2','S_IMPNG_EM',2020,71105.9090909091);
INSERT INTO "Output_Emissions" VALUES ('R1','test_run','supply',2025,'CO2','S_IMPNG_EM',2020,29494.0909090909);
INSERT INTO "Output_Emissions" VALUES ('R1','test_run','supply',2020,'CO2','S_IMPNG_EM',2020,26750.4545454545);
INSERT INTO "Output_Emissions" VALUES ('R2','test_run','supply',2020,'CO2','S_IMPNG_EM',2020,64704.0909090909);
INSERT INTO "Output_Objective" VALUES ('test_run','TotalCost',139031.85443157);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'winter','night','ELC','E_DIST',2015,'ELCD',308.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2025,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',562.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'spring','night','ELC','E_DIST',2015,'ELCD',77.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2025,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',57.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',65.9090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',215.909090909091);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',57.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'spring','day','ELC','E_DIST',2015,'ELCD',15.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',25.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'spring','day','ELC','E_DIST',2015,'ELCD',16.5);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',27.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',72.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',65.9090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2025,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',27.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2020,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',52.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'winter','day','ELC','E_DIST',2015,'ELCD',99.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2025,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',422.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'winter','day','ELC','E_DIST',2015,'ELCD',90.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',511.363636363636);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'winter','night','ELC','E_DIST',2015,'ELCD',132.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'fall','day','ELC','E_DIST',2015,'ELCD',15.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2025,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',142.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'fall','day','ELC','E_DIST',2015,'ELCD',35.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2020,'fall','day','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'spring','night','ELC','E_DIST',2015,'ELCD',30.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2020,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',129.545454545455);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'winter','night','ELC','E_DIST',2015,'ELCD',120.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2020,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',25.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'fall','night','ELC','E_DIST',2015,'ELCD',70.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2025,'fall','day','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'spring','day','ELC','E_DIST',2015,'ELCD',38.5);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2025,'ELC',50.9090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'spring','night','ELC','E_DIST',2015,'ELCD',70.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2025,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',57.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',215.909090909091);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',25.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2020,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',384.090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',161.363636363636);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',129.545454545455);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',142.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',177.727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'spring','night','ELC','E_DIST',2015,'ELCD',33.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',57.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2025,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',177.727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2025,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',237.727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',52.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2020,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',65.9090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',129.545454545455);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',384.090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2020,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',52.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2025,'spring','night','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2020,'spring','day','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',511.363636363636);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2020,'winter','night','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'winter','day','ELC','E_DIST',2015,'ELCD',210.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2025,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',72.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2025,'fall','night','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',27.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2025,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',72.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2020,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',511.363636363636);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'winter','night','ELC','E_DIST',2015,'ELCD',280.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'fall','night','ELC','E_DIST',2015,'ELCD',33.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2025,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',142.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2025,'winter','day','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'winter','day','ELC','E_DIST',2015,'ELCD',231.0);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2020,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',25.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2020,'winter','day','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2020,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',129.545454545455);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'fall','day','ELC','E_DIST',2015,'ELCD',16.5);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2020,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',161.363636363636);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',422.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2025,'winter','night','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'fall','day','ELC','E_DIST',2015,'ELCD',38.5);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','supply',2020,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',65.9090909090909);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',72.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2025,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',27.7272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','supply',2020,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',215.909090909091);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',52.2727272727273);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2020,'spring','day','ELC','E_DIST',2015,'ELCD',35.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2020,'spring','night','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2020,'fall','night','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2025,'ELC',21.8181818181818);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',142.272727272727);
INSERT INTO "Output_VFlow_In" VALUES ('R2','test_run','electric',2025,'fall','night','ELC','E_DIST',2015,'ELCD',77.0);
INSERT INTO "Output_VFlow_In" VALUES ('R2-R1','test_run','electric',2025,'spring','day','ELC','E_TRANS',2015,'ELC',1.38888888888889);
INSERT INTO "Output_VFlow_In" VALUES ('R1','test_run','electric',2020,'fall','night','ELC','E_DIST',2015,'ELCD',30.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'winter','night','ELC','E_DIST',2015,'ELCD',308.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2025,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',562.272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'spring','night','ELC','E_DIST',2015,'ELCD',77.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2025,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',57.7272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',36.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',118.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',31.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'spring','day','ELC','E_DIST',2015,'ELCD',15.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',13.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'spring','day','ELC','E_DIST',2015,'ELCD',16.5);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',15.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',39.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'fall','day','NG_EM','E_NGCC_EM',2020,'ELC',36.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2025,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',27.7272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2020,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',52.2727272727273);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'winter','day','ELC','E_DIST',2015,'ELCD',99.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2025,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',422.272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'winter','day','ELC','E_DIST',2015,'ELCD',90.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',281.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'winter','night','ELC','E_DIST',2015,'ELCD',132.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'fall','day','ELC','E_DIST',2015,'ELCD',15.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2025,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',142.272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'fall','day','ELC','E_DIST',2015,'ELCD',35.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2020,'fall','day','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'spring','night','ELC','E_DIST',2015,'ELCD',30.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2020,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',129.545454545455);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'winter','night','ELC','E_DIST',2015,'ELCD',120.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2020,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',25.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'fall','night','ELC','E_DIST',2015,'ELCD',70.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2025,'fall','day','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'spring','day','ELC','E_DIST',2015,'ELCD',38.5);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2025,'ELC',28.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'spring','night','ELC','E_DIST',2015,'ELCD',70.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2025,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',57.7272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',118.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',13.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2020,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',384.090909090909);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',88.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',71.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',78.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',97.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'spring','night','ELC','E_DIST',2015,'ELCD',33.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',31.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2025,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',177.727272727273);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2025,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',237.727272727273);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'fall','night','NG_EM','E_NGCC_EM',2020,'ELC',28.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2020,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',65.9090909090909);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',71.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',211.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2020,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',52.2727272727273);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2025,'spring','night','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2020,'spring','day','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'winter','night','NG_EM','E_NGCC_EM',2020,'ELC',281.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2020,'winter','night','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'winter','day','ELC','E_DIST',2015,'ELCD',210.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2025,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',72.2727272727273);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2025,'fall','night','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',15.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2025,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',72.2727272727273);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2020,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',511.363636363636);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'winter','night','ELC','E_DIST',2015,'ELCD',280.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'fall','night','ELC','E_DIST',2015,'ELCD',33.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2025,'fall','night','ethos','S_IMPNG_EM',2020,'NG_EM',142.272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2025,'winter','day','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'winter','day','ELC','E_DIST',2015,'ELCD',231.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2020,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',25.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2020,'winter','day','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2020,'spring','night','ethos','S_IMPNG_EM',2020,'NG_EM',129.545454545455);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'fall','day','ELC','E_DIST',2015,'ELCD',16.5);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2020,'winter','day','ethos','S_IMPNG_EM',2020,'NG_EM',161.363636363636);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'winter','day','NG_EM','E_NGCC_EM',2020,'ELC',232.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2025,'winter','night','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'fall','day','ELC','E_DIST',2015,'ELCD',38.5);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','supply',2020,'spring','day','ethos','S_IMPNG_EM',2020,'NG_EM',65.9090909090909);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'spring','day','NG_EM','E_NGCC_EM',2020,'ELC',39.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2025,'fall','day','ethos','S_IMPNG_EM',2020,'NG_EM',27.7272727272727);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','supply',2020,'winter','night','ethos','S_IMPNG_EM',2020,'NG_EM',215.909090909091);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',28.75);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2020,'spring','day','ELC','E_DIST',2015,'ELCD',35.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2020,'spring','night','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2020,'fall','night','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2025,'winter','night','NG_EM','E_NGCC_EM',2025,'ELC',12.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'spring','night','NG_EM','E_NGCC_EM',2020,'ELC',78.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R2','test_run','electric',2025,'fall','night','ELC','E_DIST',2015,'ELCD',77.0);
INSERT INTO "Output_VFlow_Out" VALUES ('R2-R1','test_run','electric',2025,'spring','day','ELC','E_TRANS',2015,'ELC',1.25);
INSERT INTO "Output_VFlow_Out" VALUES ('R1','test_run','electric',2020,'fall','night','ELC','E_DIST',2015,'ELCD',30.0);
INSERT INTO "Output_V_Capacity" VALUES ('R2-R1','test_run','electric','E_TRANS',2015,10.0);
INSERT INTO "Output_V_Capacity" VALUES ('R2','test_run','electric','E_NGCC_EM',2025,7.10209258084972);
INSERT INTO "Output_V_Capacity" VALUES ('R1','test_run','supply','S_IMPNG_EM',2020,1901.81818181818);
INSERT INTO "Output_V_Capacity" VALUES ('R1-R2','test_run','electric','E_TRANS',2015,10.0);
INSERT INTO "Output_V_Capacity" VALUES ('R1','test_run','electric','E_NGCC_EM',2025,3.0437539632213);
INSERT INTO "Output_V_Capacity" VALUES ('R2','test_run','electric','E_DIST',2015,1000.0);
INSERT INTO "Output_V_Capacity" VALUES ('R1','test_run','electric','E_NGCC_EM',2020,30.1204819277108);
INSERT INTO "Output_V_Capacity" VALUES ('R1','test_run','electric','E_DIST',2015,1000.0);
INSERT INTO "Output_V_Capacity" VALUES ('R2','test_run','supply','S_IMPNG_EM',2020,4498.18181818182);
INSERT INTO "Output_V_Capacity" VALUES ('R2','test_run','electric','E_NGCC_EM',2020,71.3379835129994);
INSERT INTO "SegFrac" VALUES ('spring','day',0.125,'Spring - Day');
INSERT INTO "SegFrac" VALUES ('spring','night',0.125,'Spring - Night');
INSERT INTO "SegFrac" VALUES ('summer','day',0.125,'Summer - Day');
INSERT INTO "SegFrac" VALUES ('summer','night',0.125,'Summer - Night');
INSERT INTO "SegFrac" VALUES ('fall','day',0.125,'Fall - Day');
INSERT INTO "SegFrac" VALUES ('fall','night',0.125,'Fall - Night');
INSERT INTO "SegFrac" VALUES ('winter','day',0.125,'Winter - Day');
INSERT INTO "SegFrac" VALUES ('winter','night',0.125,'Winter - Night');
INSERT INTO "commodities" VALUES ('ethos','p','dummy');
INSERT INTO "commodities" VALUES ('NG','p','natural gas');
INSERT INTO "commodities" VALUES ('NG_EM','p','natural gas');
INSERT INTO "commodities" VALUES ('ELC','p','electricity');
INSERT INTO "commodities" VALUES ('ELCD','d','electricity');
INSERT INTO "commodities" VALUES ('CO2','e','CO2 emissions commodity');
INSERT INTO "commodity_labels" VALUES ('p','physical commodity');
INSERT INTO "commodity_labels" VALUES ('e','emissions commodity');
INSERT INTO "commodity_labels" VALUES ('d','demand commodity');
INSERT INTO "regions" VALUES ('R1',NULL);
INSERT INTO "regions" VALUES ('R2',NULL);
INSERT INTO "sector_labels" VALUES ('supply');
INSERT INTO "sector_labels" VALUES ('electric');
INSERT INTO "tech_exchange" VALUES ('E_TRANS','');
INSERT INTO "technologies" VALUES ('S_IMPNG_EM','r','supply',' imported natural gas','');
INSERT INTO "technologies" VALUES ('S_IMPNG','r','supply',' imported natural gas','');
INSERT INTO "technologies" VALUES ('E_NGCC_EM','p','electric',' natural gas combined-cycle','');
INSERT INTO "technologies" VALUES ('E_NGCC','p','electric',' natural gas combined-cycle','');
INSERT INTO "technologies" VALUES ('E_TRANS','p','electric','electric transmission','');
INSERT INTO "technologies" VALUES ('E_DIST','p','electric','electric transmission','');
INSERT INTO "technology_labels" VALUES ('r','resource technology');
INSERT INTO "technology_labels" VALUES ('p','production technology');
INSERT INTO "technology_labels" VALUES ('pb','baseload production technology');
INSERT INTO "technology_labels" VALUES ('ps','storage production technology');
INSERT INTO "time_of_day" VALUES ('day');
INSERT INTO "time_of_day" VALUES ('night');
INSERT INTO "time_period_labels" VALUES ('e','existing vintages');
INSERT INTO "time_period_labels" VALUES ('f','future');
INSERT INTO "time_periods" VALUES (2015,'e');
INSERT INTO "time_periods" VALUES (2020,'f');
INSERT INTO "time_periods" VALUES (2025,'f');
INSERT INTO "time_periods" VALUES (2030,'f');
INSERT INTO "time_season" VALUES ('spring');
INSERT INTO "time_season" VALUES ('summer');
INSERT INTO "time_season" VALUES ('fall');
INSERT INTO "time_season" VALUES ('winter');
COMMIT;
