BEGIN TRANSACTION;
CREATE TABLE "time_season" (
	"t_season"	text,
	PRIMARY KEY("t_season")
);
INSERT INTO `time_season` VALUES ('spring');
INSERT INTO `time_season` VALUES ('summer');
INSERT INTO `time_season` VALUES ('fall');
INSERT INTO `time_season` VALUES ('winter');
CREATE TABLE "time_periods" (
	"t_periods"	integer,
	"flag"	text,
	PRIMARY KEY("t_periods"),
	FOREIGN KEY("flag") REFERENCES "time_period_labels"("t_period_labels")
);
INSERT INTO `time_periods` VALUES (2015,'e');
INSERT INTO `time_periods` VALUES (2020,'f');
INSERT INTO `time_periods` VALUES (2025,'f');
INSERT INTO `time_periods` VALUES (2030,'f');
INSERT INTO `time_periods` VALUES (2035,'f');
CREATE TABLE "time_period_labels" (
	"t_period_labels"	text,
	"t_period_labels_desc"	text,
	PRIMARY KEY("t_period_labels")
);
INSERT INTO `time_period_labels` VALUES ('e','existing vintages');
INSERT INTO `time_period_labels` VALUES ('f','future');
CREATE TABLE "time_of_day" (
	"t_day"	text,
	PRIMARY KEY("t_day")
);
INSERT INTO `time_of_day` VALUES ('day');
INSERT INTO `time_of_day` VALUES ('night');
CREATE TABLE "technology_labels" (
	"tech_labels"	text,
	"tech_labels_desc"	text,
	PRIMARY KEY("tech_labels")
);
INSERT INTO `technology_labels` VALUES ('r','resource technology');
INSERT INTO `technology_labels` VALUES ('p','production technology');
INSERT INTO `technology_labels` VALUES ('pb','baseload production technology');
INSERT INTO `technology_labels` VALUES ('ps','storage production technology');
CREATE TABLE "technologies" (
	"tech"	text,
	"flag"	text,
	"sector"	text,
	"tech_desc"	text,
	"tech_category"	text,
	PRIMARY KEY("tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("flag") REFERENCES "technology_labels"("tech_labels")
);
INSERT INTO `technologies` VALUES ('S_IMPETH','r','supply',' imported ethanol','');
INSERT INTO `technologies` VALUES ('S_IMPOIL','r','supply',' imported crude oil','');
INSERT INTO `technologies` VALUES ('S_IMPNG','r','supply',' imported natural gas','');
INSERT INTO `technologies` VALUES ('S_IMPURN','r','supply',' imported uranium','');
INSERT INTO `technologies` VALUES ('S_OILREF','p','supply',' crude oil refinery','');
INSERT INTO `technologies` VALUES ('E_NGCC','p','electric',' natural gas combined-cycle','');
INSERT INTO `technologies` VALUES ('E_SOLPV','p','electric',' solar photovoltaic','');
INSERT INTO `technologies` VALUES ('E_BATT','ps','electric',' lithium-ion battery','');
INSERT INTO `technologies` VALUES ('E_NUCLEAR','pb','electric',' nuclear power plant','');
INSERT INTO `technologies` VALUES ('T_BLND','p','transport','ethanol - gasoline blending process','');
INSERT INTO `technologies` VALUES ('T_DSL','p','transport','diesel vehicle','');
INSERT INTO `technologies` VALUES ('T_GSL','p','transport','gasoline vehicle','');
INSERT INTO `technologies` VALUES ('T_EV','p','transport','electric vehicle','');
INSERT INTO `technologies` VALUES ('R_EH','p','residential',' electric residential heating','');
INSERT INTO `technologies` VALUES ('R_NGH','p','residential',' natural gas residential heating','');
INSERT INTO `technologies` VALUES ('E_TRANS','p','electric','electric transmission','');
CREATE TABLE "tech_reserve" (
	"tech"	text,
	"notes"	text,
	PRIMARY KEY("tech")
);
CREATE TABLE "tech_exchange" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
INSERT INTO `tech_exchange` VALUES ('E_TRANS','');
CREATE TABLE "tech_curtailment" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE "tech_flex" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
INSERT INTO `tech_curtailment` VALUES ('S_OILREF',NULL);
CREATE TABLE "tech_annual" (
	"tech"	text,
	"notes"	TEXT,
	PRIMARY KEY("tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE "sector_labels" (
	"sector"	text,
	PRIMARY KEY("sector")
);
INSERT INTO `sector_labels` VALUES ('supply');
INSERT INTO `sector_labels` VALUES ('electric');
INSERT INTO `sector_labels` VALUES ('transport');
INSERT INTO `sector_labels` VALUES ('commercial');
INSERT INTO `sector_labels` VALUES ('residential');
INSERT INTO `sector_labels` VALUES ('industrial');
CREATE TABLE "regions" (
	"regions"	TEXT,
	"region_note"	TEXT,
	PRIMARY KEY("regions")
);
INSERT INTO `regions` VALUES ('R1',NULL);
INSERT INTO `regions` VALUES ('R2',NULL);
CREATE TABLE "groups" (
	"group_name"	text,
	"notes"	text,
	PRIMARY KEY("group_name")
);
CREATE TABLE "commodity_labels" (
	"comm_labels"	text,
	"comm_labels_desc"	text,
	PRIMARY KEY("comm_labels")
);
INSERT INTO `commodity_labels` VALUES ('p','physical commodity');
INSERT INTO `commodity_labels` VALUES ('e','emissions commodity');
INSERT INTO `commodity_labels` VALUES ('d','demand commodity');
CREATE TABLE "commodities" (
	"comm_name"	text,
	"flag"	text,
	"comm_desc"	text,
	PRIMARY KEY("comm_name"),
	FOREIGN KEY("flag") REFERENCES "commodity_labels"("comm_labels")
);
INSERT INTO `commodities` VALUES ('ethos','p','dummy commodity to supply inputs (makes graph easier to read)');
INSERT INTO `commodities` VALUES ('OIL','p','crude oil');
INSERT INTO `commodities` VALUES ('NG','p','natural gas');
INSERT INTO `commodities` VALUES ('URN','p','uranium');
INSERT INTO `commodities` VALUES ('ETH','p','ethanol');
INSERT INTO `commodities` VALUES ('SOL','p','solar insolation');
INSERT INTO `commodities` VALUES ('GSL','p','gasoline');
INSERT INTO `commodities` VALUES ('DSL','p','diesel');
INSERT INTO `commodities` VALUES ('ELC','p','electricity');
INSERT INTO `commodities` VALUES ('E10','p','gasoline blend with 10% ethanol');
INSERT INTO `commodities` VALUES ('VMT','d','travel demand for vehicle-miles traveled');
INSERT INTO `commodities` VALUES ('RH','d','demand for residential heating');
INSERT INTO `commodities` VALUES ('CO2','e','CO2 emissions commodity');
CREATE TABLE "TechOutputSplit" (
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
INSERT INTO `TechOutputSplit` VALUES ('R1',2020,'S_OILREF','GSL',0.9,'');
INSERT INTO `TechOutputSplit` VALUES ('R1',2020,'S_OILREF','DSL',0.1,'');
INSERT INTO `TechOutputSplit` VALUES ('R1',2025,'S_OILREF','GSL',0.9,'');
INSERT INTO `TechOutputSplit` VALUES ('R1',2025,'S_OILREF','DSL',0.1,'');
INSERT INTO `TechOutputSplit` VALUES ('R1',2030,'S_OILREF','GSL',0.9,'');
INSERT INTO `TechOutputSplit` VALUES ('R1',2030,'S_OILREF','DSL',0.1,'');
INSERT INTO `TechOutputSplit` VALUES ('R2',2020,'S_OILREF','GSL',0.72,'');
INSERT INTO `TechOutputSplit` VALUES ('R2',2020,'S_OILREF','DSL',0.08,'');
INSERT INTO `TechOutputSplit` VALUES ('R2',2025,'S_OILREF','GSL',0.72,'');
INSERT INTO `TechOutputSplit` VALUES ('R2',2025,'S_OILREF','DSL',0.08,'');
INSERT INTO `TechOutputSplit` VALUES ('R2',2030,'S_OILREF','GSL',0.72,'');
INSERT INTO `TechOutputSplit` VALUES ('R2',2030,'S_OILREF','DSL',0.08,'');
CREATE TABLE "TechInputSplit" (
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
INSERT INTO `TechInputSplit` VALUES ('R1',2020,'GSL','T_BLND',0.9,'');
INSERT INTO `TechInputSplit` VALUES ('R1',2020,'ETH','T_BLND',0.1,'');
INSERT INTO `TechInputSplit` VALUES ('R1',2025,'GSL','T_BLND',0.9,'');
INSERT INTO `TechInputSplit` VALUES ('R1',2025,'ETH','T_BLND',0.1,'');
INSERT INTO `TechInputSplit` VALUES ('R1',2030,'GSL','T_BLND',0.9,'');
INSERT INTO `TechInputSplit` VALUES ('R1',2030,'ETH','T_BLND',0.1,'');
INSERT INTO `TechInputSplit` VALUES ('R2',2020,'GSL','T_BLND',0.72,'');
INSERT INTO `TechInputSplit` VALUES ('R2',2020,'ETH','T_BLND',0.08,'');
INSERT INTO `TechInputSplit` VALUES ('R2',2025,'GSL','T_BLND',0.72,'');
INSERT INTO `TechInputSplit` VALUES ('R2',2025,'ETH','T_BLND',0.08,'');
INSERT INTO `TechInputSplit` VALUES ('R2',2030,'GSL','T_BLND',0.72,'');
INSERT INTO `TechInputSplit` VALUES ('R2',2030,'ETH','T_BLND',0.08,'');
CREATE TABLE "StorageDuration" (
	"regions"	text,
	"tech"	text,
	"duration"	real,
	"duration_notes"	text,
	PRIMARY KEY("regions","tech")
);
INSERT INTO `StorageDuration` VALUES ('R1','E_BATT',8.0,'8-hour duration specified as fraction of a day');
INSERT INTO `StorageDuration` VALUES ('R2','E_BATT',8.0,'8-hour duration specified as fraction of a day');
CREATE TABLE "SegFrac" (
	"season_name"	text,
	"time_of_day_name"	text,
	"segfrac"	real CHECK("segfrac" >= 0 AND "segfrac" <= 1),
	"segfrac_notes"	text,
	PRIMARY KEY("season_name","time_of_day_name"),
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day")
);
INSERT INTO `SegFrac` VALUES ('spring','day',0.125,'Spring - Day');
INSERT INTO `SegFrac` VALUES ('spring','night',0.125,'Spring - Night');
INSERT INTO `SegFrac` VALUES ('summer','day',0.125,'Summer - Day');
INSERT INTO `SegFrac` VALUES ('summer','night',0.125,'Summer - Night');
INSERT INTO `SegFrac` VALUES ('fall','day',0.125,'Fall - Day');
INSERT INTO `SegFrac` VALUES ('fall','night',0.125,'Fall - Night');
INSERT INTO `SegFrac` VALUES ('winter','day',0.125,'Winter - Day');
INSERT INTO `SegFrac` VALUES ('winter','night',0.125,'Winter - Night');
CREATE TABLE "PlanningReserveMargin" (
	`regions`	text,
	`reserve_margin`	REAL,
	PRIMARY KEY(regions),
	FOREIGN KEY(`regions`) REFERENCES regions
);
CREATE TABLE "Output_V_Capacity" (
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
CREATE TABLE "Output_VFlow_Out" (
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
CREATE TABLE "Output_VFlow_In" (
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
CREATE TABLE "Output_Objective" (
	"scenario"	text,
	"objective_name"	text,
	"total_system_cost"	real
);
CREATE TABLE "Output_Emissions" (
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
CREATE TABLE "Output_Curtailment" (
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
CREATE TABLE "Output_Costs" (
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
CREATE TABLE "Output_Duals" (
	"constraint_name"	text,
	"scenario"	text,
	"dual"	real,
	PRIMARY KEY("constraint_name","scenario")
);
CREATE TABLE "Output_CapacityByPeriodAndTech" (
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
CREATE TABLE "MyopicBaseyear" (
	"year"	real
	"notes"	text	
);
CREATE TABLE "MinGenGroupWeight" (
	"regions"	text,
	"tech"	text,
	"group_name"	text,
	"act_fraction"	REAL,
	"tech_desc"	text,
	PRIMARY KEY("tech","group_name","regions")
);
CREATE TABLE "MinGenGroupTarget" (
	"regions"	text,
	"periods"	integer,
	"group_name"	text,
	"min_act_g"	real,
	"notes"	text,
	PRIMARY KEY("periods","group_name","regions")
);
CREATE TABLE "MinCapacity" (
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
CREATE TABLE "MinActivity" (
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
INSERT INTO `MinActivity` VALUES ('R1',2020,'T_GSL',35.0,'','');
INSERT INTO `MinActivity` VALUES ('R1',2025,'T_GSL',35.0,'','');
INSERT INTO `MinActivity` VALUES ('R1',2030,'T_GSL',35.0,'','');
INSERT INTO `MinActivity` VALUES ('R2',2020,'T_GSL',15.0,'','');
INSERT INTO `MinActivity` VALUES ('R2',2025,'T_GSL',15.0,'','');
INSERT INTO `MinActivity` VALUES ('R2',2030,'T_GSL',15.0,'','');
CREATE TABLE "MaxCapacity" (
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
CREATE TABLE "MaxActivity" (
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
CREATE TABLE "LifetimeTech" (
	"regions"	text,
	"tech"	text,
	"life"	real,
	"life_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
INSERT INTO `LifetimeTech` VALUES ('R1','S_IMPETH',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','S_IMPOIL',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','S_IMPNG',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','S_IMPURN',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','S_OILREF',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','E_NGCC',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','E_SOLPV',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','E_BATT',20.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','E_NUCLEAR',50.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','T_BLND',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','T_DSL',12.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','T_GSL',12.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','T_EV',12.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','R_EH',20.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1','R_NGH',20.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','S_IMPETH',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','S_IMPOIL',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','S_IMPNG',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','S_IMPURN',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','S_OILREF',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','E_NGCC',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','E_SOLPV',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','E_BATT',20.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','E_NUCLEAR',50.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','T_BLND',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','T_DSL',12.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','T_GSL',12.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','T_EV',12.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','R_EH',20.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2','R_NGH',20.0,'');
INSERT INTO `LifetimeTech` VALUES ('R1-R2','E_TRANS',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('R2-R1','E_TRANS',30.0,'');
CREATE TABLE "LifetimeProcess" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"life_process"	real,
	"life_process_notes"	text,
	PRIMARY KEY("regions","tech","vintage"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE "LifetimeLoanTech" (
	"regions"	text,
	"tech"	text,
	"loan"	real,
	"loan_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
INSERT INTO `LifetimeLoanTech` VALUES ('R1','S_IMPETH',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','S_IMPOIL',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','S_IMPNG',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','S_IMPURN',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','S_OILREF',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','E_NGCC',30.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','E_SOLPV',30.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','E_BATT',20.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','E_NUCLEAR',50.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','T_BLND',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','T_DSL',12.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','T_GSL',12.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','T_EV',12.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','R_EH',20.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R1','R_NGH',20.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','S_IMPETH',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','S_IMPOIL',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','S_IMPNG',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','S_IMPURN',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','S_OILREF',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','E_NGCC',30.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','E_SOLPV',30.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','E_BATT',20.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','E_NUCLEAR',50.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','T_BLND',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','T_DSL',12.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','T_GSL',12.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','T_EV',12.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','R_EH',20.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('R2','R_NGH',20.0,'');
CREATE TABLE "GrowthRateSeed" (
	"regions"	text,
	"tech"	text,
	"growthrate_seed"	real,
	"growthrate_seed_units"	text,
	"growthrate_seed_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE "GrowthRateMax" (
	"regions"	text,
	"tech"	text,
	"growthrate_max"	real,
	"growthrate_max_notes"	text,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE "GlobalDiscountRate" (
	"rate"	real
);
INSERT INTO `GlobalDiscountRate` VALUES (0.05);
CREATE TABLE "ExistingCapacity" (
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
INSERT INTO `ExistingCapacity` VALUES ('R1','E_NUCLEAR',2015,0.07,'GW','');
INSERT INTO `ExistingCapacity` VALUES ('R2','E_NUCLEAR',2015,0.03,'GW','');
INSERT INTO `ExistingCapacity` VALUES ('R1-R2','E_TRANS',2015,10.0,'GW','');
INSERT INTO `ExistingCapacity` VALUES ('R2-R1','E_TRANS',2015,10.0,'GW','');
CREATE TABLE "EmissionLimit" (
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
INSERT INTO `EmissionLimit` VALUES ('R1',2020,'CO2',25000.0,'kT CO2','');
INSERT INTO `EmissionLimit` VALUES ('R1',2025,'CO2',24000.0,'kT CO2','');
INSERT INTO `EmissionLimit` VALUES ('R1',2030,'CO2',23000.0,'kT CO2','');
INSERT INTO `EmissionLimit` VALUES ('global',2020,'CO2',37500.0,'kT CO2','');
INSERT INTO `EmissionLimit` VALUES ('global',2025,'CO2',36000.0,'kT CO2','');
INSERT INTO `EmissionLimit` VALUES ('global',2030,'CO2',34500.0,'kT CO2','');
CREATE TABLE "EmissionActivity" (
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
INSERT INTO `EmissionActivity` VALUES ('R1','CO2','ethos','S_IMPNG',2020,'NG',50.3,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO `EmissionActivity` VALUES ('R1','CO2','OIL','S_OILREF',2020,'GSL',67.2,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO `EmissionActivity` VALUES ('R1','CO2','OIL','S_OILREF',2020,'DSL',69.4,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO `EmissionActivity` VALUES ('R2','CO2','ethos','S_IMPNG',2020,'NG',50.3,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO `EmissionActivity` VALUES ('R2','CO2','OIL','S_OILREF',2020,'GSL',67.2,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO `EmissionActivity` VALUES ('R2','CO2','OIL','S_OILREF',2020,'DSL',69.4,'kT/PJ','taken from MIT Energy Fact Sheet');
CREATE TABLE "Efficiency" (
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
INSERT INTO `Efficiency` VALUES ('R1','ethos','S_IMPETH',2020,'ETH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','ethos','S_IMPOIL',2020,'OIL',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','ethos','S_IMPURN',2020,'URN',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','OIL','S_OILREF',2020,'GSL',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','OIL','S_OILREF',2020,'DSL',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','ETH','T_BLND',2020,'E10',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','GSL','T_BLND',2020,'E10',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','NG','E_NGCC',2020,'ELC',0.55,'');
INSERT INTO `Efficiency` VALUES ('R1','NG','E_NGCC',2025,'ELC',0.55,'');
INSERT INTO `Efficiency` VALUES ('R1','NG','E_NGCC',2030,'ELC',0.55,'');
INSERT INTO `Efficiency` VALUES ('R1','SOL','E_SOLPV',2020,'ELC',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','SOL','E_SOLPV',2025,'ELC',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','SOL','E_SOLPV',2030,'ELC',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','URN','E_NUCLEAR',2015,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R1','URN','E_NUCLEAR',2020,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R1','URN','E_NUCLEAR',2025,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R1','URN','E_NUCLEAR',2030,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','E_BATT',2020,'ELC',0.85,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','E_BATT',2025,'ELC',0.85,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','E_BATT',2030,'ELC',0.85,'');
INSERT INTO `Efficiency` VALUES ('R1','E10','T_GSL',2020,'VMT',0.25,'');
INSERT INTO `Efficiency` VALUES ('R1','E10','T_GSL',2025,'VMT',0.25,'');
INSERT INTO `Efficiency` VALUES ('R1','E10','T_GSL',2030,'VMT',0.25,'');
INSERT INTO `Efficiency` VALUES ('R1','DSL','T_DSL',2020,'VMT',0.3,'');
INSERT INTO `Efficiency` VALUES ('R1','DSL','T_DSL',2025,'VMT',0.3,'');
INSERT INTO `Efficiency` VALUES ('R1','DSL','T_DSL',2030,'VMT',0.3,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','T_EV',2020,'VMT',0.89,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','T_EV',2025,'VMT',0.89,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','T_EV',2030,'VMT',0.89,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','R_EH',2020,'RH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','R_EH',2025,'RH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','ELC','R_EH',2030,'RH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R1','NG','R_NGH',2020,'RH',0.85,'');
INSERT INTO `Efficiency` VALUES ('R1','NG','R_NGH',2025,'RH',0.85,'');
INSERT INTO `Efficiency` VALUES ('R1','NG','R_NGH',2030,'RH',0.85,'');
INSERT INTO `Efficiency` VALUES ('R2','ethos','S_IMPETH',2020,'ETH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','ethos','S_IMPOIL',2020,'OIL',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','ethos','S_IMPURN',2020,'URN',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','OIL','S_OILREF',2020,'GSL',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','OIL','S_OILREF',2020,'DSL',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','ETH','T_BLND',2020,'E10',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','GSL','T_BLND',2020,'E10',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','NG','E_NGCC',2020,'ELC',0.55,'');
INSERT INTO `Efficiency` VALUES ('R2','NG','E_NGCC',2025,'ELC',0.55,'');
INSERT INTO `Efficiency` VALUES ('R2','NG','E_NGCC',2030,'ELC',0.55,'');
INSERT INTO `Efficiency` VALUES ('R2','SOL','E_SOLPV',2020,'ELC',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','SOL','E_SOLPV',2025,'ELC',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','SOL','E_SOLPV',2030,'ELC',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','URN','E_NUCLEAR',2015,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R2','URN','E_NUCLEAR',2020,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R2','URN','E_NUCLEAR',2025,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R2','URN','E_NUCLEAR',2030,'ELC',0.4,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','E_BATT',2020,'ELC',0.85,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','E_BATT',2025,'ELC',0.85,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','E_BATT',2030,'ELC',0.85,'');
INSERT INTO `Efficiency` VALUES ('R2','E10','T_GSL',2020,'VMT',0.25,'');
INSERT INTO `Efficiency` VALUES ('R2','E10','T_GSL',2025,'VMT',0.25,'');
INSERT INTO `Efficiency` VALUES ('R2','E10','T_GSL',2030,'VMT',0.25,'');
INSERT INTO `Efficiency` VALUES ('R2','DSL','T_DSL',2020,'VMT',0.3,'');
INSERT INTO `Efficiency` VALUES ('R2','DSL','T_DSL',2025,'VMT',0.3,'');
INSERT INTO `Efficiency` VALUES ('R2','DSL','T_DSL',2030,'VMT',0.3,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','T_EV',2020,'VMT',0.89,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','T_EV',2025,'VMT',0.89,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','T_EV',2030,'VMT',0.89,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','R_EH',2020,'RH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','R_EH',2025,'RH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','ELC','R_EH',2030,'RH',1.0,'');
INSERT INTO `Efficiency` VALUES ('R2','NG','R_NGH',2020,'RH',0.85,'');
INSERT INTO `Efficiency` VALUES ('R2','NG','R_NGH',2025,'RH',0.85,'');
INSERT INTO `Efficiency` VALUES ('R2','NG','R_NGH',2030,'RH',0.85,'');
INSERT INTO `Efficiency` VALUES ('R1-R2','ELC','E_TRANS',2015,'ELC',0.9,'');
INSERT INTO `Efficiency` VALUES ('R2-R1','ELC','E_TRANS',2015,'ELC',0.9,'');
CREATE TABLE "DiscountRate" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"tech_rate"	real,
	"tech_rate_notes"	text,
	PRIMARY KEY("regions","tech","vintage"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
CREATE TABLE "DemandSpecificDistribution" (
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
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','spring','day','RH',0.05,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','spring','night','RH',0.1,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','summer','day','RH',0.0,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','summer','night','RH',0.0,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','fall','day','RH',0.05,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','fall','night','RH',0.1,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','winter','day','RH',0.3,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R1','winter','night','RH',0.4,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','spring','day','RH',0.05,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','spring','night','RH',0.1,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','summer','day','RH',0.0,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','summer','night','RH',0.0,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','fall','day','RH',0.05,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','fall','night','RH',0.1,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','winter','day','RH',0.3,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('R2','winter','night','RH',0.4,'');
CREATE TABLE "Demand" (
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
INSERT INTO `Demand` VALUES ('R1',2020,'RH',30.0,'','');
INSERT INTO `Demand` VALUES ('R1',2025,'RH',33.0,'','');
INSERT INTO `Demand` VALUES ('R1',2030,'RH',36.0,'','');
INSERT INTO `Demand` VALUES ('R1',2020,'VMT',84.0,'','');
INSERT INTO `Demand` VALUES ('R1',2025,'VMT',91.0,'','');
INSERT INTO `Demand` VALUES ('R1',2030,'VMT',98.0,'','');
INSERT INTO `Demand` VALUES ('R2',2020,'RH',70.0,'','');
INSERT INTO `Demand` VALUES ('R2',2025,'RH',77.0,'','');
INSERT INTO `Demand` VALUES ('R2',2030,'RH',84.0,'','');
INSERT INTO `Demand` VALUES ('R2',2020,'VMT',36.0,'','');
INSERT INTO `Demand` VALUES ('R2',2025,'VMT',39.0,'','');
INSERT INTO `Demand` VALUES ('R2',2030,'VMT',42.0,'','');
CREATE TABLE "CostVariable" (
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
INSERT INTO `CostVariable` VALUES ('R1',2020,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2020,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2020,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2020,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2020,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'E_NGCC',2025,1.7,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'E_NGCC',2025,1.7,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'E_NGCC',2030,1.8,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2020,'E_NUCLEAR',2020,0.24,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'E_NUCLEAR',2020,0.24,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2025,'E_NUCLEAR',2025,0.25,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'E_NUCLEAR',2020,0.24,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'E_NUCLEAR',2025,0.25,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1',2030,'E_NUCLEAR',2030,0.26,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2020,'S_IMPETH',2020,25.6,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'S_IMPETH',2020,25.6,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'S_IMPETH',2020,25.6,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2020,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2020,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2020,'S_OILREF',2020,0.8,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'S_OILREF',2020,0.8,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'S_OILREF',2020,0.8,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2020,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'E_NGCC',2025,1.36,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'E_NGCC',2025,1.36,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'E_NGCC',2030,1.44,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2020,'E_NUCLEAR',2020,0.192,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'E_NUCLEAR',2020,0.192,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2025,'E_NUCLEAR',2025,0.2,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'E_NUCLEAR',2020,0.192,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'E_NUCLEAR',2025,0.2,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2',2030,'E_NUCLEAR',2030,0.208,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1-R2',2020,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1-R2',2025,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R1-R2',2030,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2-R1',2020,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2-R1',2025,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO `CostVariable` VALUES ('R2-R1',2030,'E_TRANS',2015,0.1,'$M/PJ','');
CREATE TABLE "CostInvest" (
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
INSERT INTO `CostInvest` VALUES ('R1','E_NGCC',2020,1050.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_NGCC',2025,1025.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_NGCC',2030,1000.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_SOLPV',2020,900.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_SOLPV',2025,560.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_SOLPV',2030,800.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_NUCLEAR',2020,6145.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_NUCLEAR',2025,6045.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_NUCLEAR',2030,5890.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_BATT',2020,1150.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_BATT',2025,720.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','E_BATT',2030,480.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R1','T_GSL',2020,2570.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_GSL',2025,2700.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_GSL',2030,2700.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_DSL',2020,2715.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_DSL',2025,2810.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_DSL',2030,2810.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_EV',2020,3100.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_EV',2025,3030.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','T_EV',2030,2925.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R1','R_EH',2020,4.1,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R1','R_EH',2025,4.1,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R1','R_EH',2030,4.1,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R1','R_NGH',2020,7.6,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R1','R_NGH',2025,7.6,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R1','R_NGH',2030,7.6,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R2','E_NGCC',2020,840.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_NGCC',2025,820.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_NGCC',2030,800.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_SOLPV',2020,720.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_SOLPV',2025,448.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_SOLPV',2030,640.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_NUCLEAR',2020,4916.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_NUCLEAR',2025,4836.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_NUCLEAR',2030,4712.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_BATT',2020,920.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_BATT',2025,576.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','E_BATT',2030,384.0,'$M/GW','');
INSERT INTO `CostInvest` VALUES ('R2','T_GSL',2020,2056.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_GSL',2025,2160.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_GSL',2030,2160.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_DSL',2020,2172.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_DSL',2025,2248.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_DSL',2030,2248.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_EV',2020,2480.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_EV',2025,2424.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','T_EV',2030,2340.0,'$/bvmt/yr','');
INSERT INTO `CostInvest` VALUES ('R2','R_EH',2020,3.28,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R2','R_EH',2025,3.28,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R2','R_EH',2030,3.28,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R2','R_NGH',2020,6.08,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R2','R_NGH',2025,6.08,'$/PJ/yr','');
INSERT INTO `CostInvest` VALUES ('R2','R_NGH',2030,6.08,'$/PJ/yr','');
CREATE TABLE "CostFixed" (
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
INSERT INTO `CostFixed` VALUES ('R1',2020,'E_NGCC',2020,30.6,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_NGCC',2020,9.78,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_NGCC',2025,9.78,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_NGCC',2020,9.78,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_NGCC',2025,9.78,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_NGCC',2030,9.78,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2020,'E_SOLPV',2020,10.4,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_SOLPV',2020,10.4,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_SOLPV',2025,9.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_SOLPV',2020,10.4,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_SOLPV',2025,9.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_SOLPV',2030,9.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2020,'E_NUCLEAR',2020,98.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_NUCLEAR',2020,98.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_NUCLEAR',2025,98.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_NUCLEAR',2020,98.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_NUCLEAR',2025,98.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_NUCLEAR',2030,98.1,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2020,'E_BATT',2020,7.05,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_BATT',2020,7.05,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2025,'E_BATT',2025,7.05,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_BATT',2020,7.05,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_BATT',2025,7.05,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R1',2030,'E_BATT',2030,7.05,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2020,'E_NGCC',2020,24.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_NGCC',2020,7.824,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_NGCC',2025,7.824,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_NGCC',2020,7.824,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_NGCC',2025,7.824,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_NGCC',2030,7.824,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2020,'E_SOLPV',2020,8.32,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_SOLPV',2020,8.32,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_SOLPV',2025,7.28,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_SOLPV',2020,8.32,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_SOLPV',2025,7.28,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_SOLPV',2030,7.28,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2020,'E_NUCLEAR',2020,78.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_NUCLEAR',2020,78.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_NUCLEAR',2025,78.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_NUCLEAR',2020,78.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_NUCLEAR',2025,78.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_NUCLEAR',2030,78.48,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2020,'E_BATT',2020,5.64,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_BATT',2020,5.64,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2025,'E_BATT',2025,5.64,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_BATT',2020,5.64,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_BATT',2025,5.64,'$M/GWyr','');
INSERT INTO `CostFixed` VALUES ('R2',2030,'E_BATT',2030,5.64,'$M/GWyr','');
CREATE TABLE "CapacityToActivity" (
	"regions"	text,
	"tech"	text,
	"c2a"	real,
	"c2a_notes"	TEXT,
	PRIMARY KEY("regions","tech"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech")
);
INSERT INTO `CapacityToActivity` VALUES ('R1','S_IMPETH',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','S_IMPOIL',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','S_IMPNG',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','S_IMPURN',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','S_OILREF',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','E_NGCC',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','E_SOLPV',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','E_BATT',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','E_NUCLEAR',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','T_BLND',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','T_DSL',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','T_GSL',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','T_EV',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','R_EH',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1','R_NGH',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','S_IMPETH',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','S_IMPOIL',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','S_IMPNG',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','S_IMPURN',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','S_OILREF',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','E_NGCC',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','E_SOLPV',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','E_BATT',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','E_NUCLEAR',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','T_BLND',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','T_DSL',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','T_GSL',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','T_EV',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','R_EH',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R2','R_NGH',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('R1-R2','E_TRANS',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('R2-R1','E_TRANS',31.54,'');
CREATE TABLE "CapacityFactorTech" (
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
INSERT INTO `CapacityFactorTech` VALUES ('R1','spring','day','E_SOLPV',0.6,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','spring','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','summer','day','E_SOLPV',0.6,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','summer','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','fall','day','E_SOLPV',0.6,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','fall','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','winter','day','E_SOLPV',0.6,'');
INSERT INTO `CapacityFactorTech` VALUES ('R1','winter','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','spring','day','E_SOLPV',0.48,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','spring','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','summer','day','E_SOLPV',0.48,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','summer','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','fall','day','E_SOLPV',0.48,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','fall','night','E_SOLPV',0.0,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','winter','day','E_SOLPV',0.48,'');
INSERT INTO `CapacityFactorTech` VALUES ('R2','winter','night','E_SOLPV',0.0,'');
CREATE TABLE "CapacityFactorProcess" (
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
CREATE TABLE "CapacityCredit" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"vintage" integer,
	"cf_tech"	real CHECK("cf_tech" >= 0 AND "cf_tech" <= 1),
	"cf_tech_notes"	text,
	PRIMARY KEY("regions","periods","tech","vintage")
);
CREATE TABLE "MaxResource" (
	"regions"	text,
	"tech"	text,
	"maxres"	real,
	"maxres_units"	text,
	"maxres_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
);
CREATE TABLE "LinkedTechs" (
	"primary_region"	text,
	"primary_tech"	text,
	"emis_comm" text, 
 	"linked_tech"	text,
	"tech_linked_notes"	text,
	FOREIGN KEY("primary_tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("linked_tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("emis_comm") REFERENCES "commodities"("comm_name"),
	PRIMARY KEY("primary_region","primary_tech", "emis_comm")
);
COMMIT;
