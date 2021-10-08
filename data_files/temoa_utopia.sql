BEGIN TRANSACTION;
CREATE TABLE "time_season" (
	"t_season"	text,
	PRIMARY KEY("t_season")
);
INSERT INTO `time_season` VALUES ('inter');
INSERT INTO `time_season` VALUES ('summer');
INSERT INTO `time_season` VALUES ('winter');
CREATE TABLE "time_periods" (
	"t_periods"	integer,
	"flag"	text,
	FOREIGN KEY("flag") REFERENCES "time_period_labels"("t_period_labels"),
	PRIMARY KEY("t_periods")
);
INSERT INTO `time_periods` VALUES (1960,'e');
INSERT INTO `time_periods` VALUES (1970,'e');
INSERT INTO `time_periods` VALUES (1980,'e');
INSERT INTO `time_periods` VALUES (1990,'f');
INSERT INTO `time_periods` VALUES (2000,'f');
INSERT INTO `time_periods` VALUES (2010,'f');
INSERT INTO `time_periods` VALUES (2020,'f');
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
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("flag") REFERENCES "technology_labels"("tech_labels"),
	PRIMARY KEY("tech")
);
INSERT INTO `technologies` VALUES ('IMPDSL1','r','supply',' imported diesel','petroleum');
INSERT INTO `technologies` VALUES ('IMPGSL1','r','supply',' imported gasoline','petroleum');
INSERT INTO `technologies` VALUES ('IMPHCO1','r','supply',' imported coal','coal');
INSERT INTO `technologies` VALUES ('IMPOIL1','r','supply',' imported crude oil','petroleum');
INSERT INTO `technologies` VALUES ('IMPURN1','r','supply',' imported uranium','uranium');
INSERT INTO `technologies` VALUES ('IMPFEQ','r','supply',' imported fossil equivalent','');
INSERT INTO `technologies` VALUES ('IMPHYD','r','supply',' imported water -- doesnt exist in Utopia','water');
INSERT INTO `technologies` VALUES ('E01','pb','electric',' coal power plant','coal');
INSERT INTO `technologies` VALUES ('E21','pb','electric',' nuclear power plant','nuclear');
INSERT INTO `technologies` VALUES ('E31','pb','electric',' hydro power','hydro');
INSERT INTO `technologies` VALUES ('E51','ps','electric',' electric storage','storage');
INSERT INTO `technologies` VALUES ('E70','p','electric',' diesel power plant','diesel');
INSERT INTO `technologies` VALUES ('RHE','p','residential',' electric residential heating','electric');
INSERT INTO `technologies` VALUES ('RHO','p','residential',' diesel residential heating','diesel');
INSERT INTO `technologies` VALUES ('RL1','p','residential',' residential lighting','electric');
INSERT INTO `technologies` VALUES ('SRE','p','supply',' crude oil processor','petroleum');
INSERT INTO `technologies` VALUES ('TXD','p','transport',' diesel powered vehicles','diesel');
INSERT INTO `technologies` VALUES ('TXE','p','transport',' electric powered vehicles','electric');
INSERT INTO `technologies` VALUES ('TXG','p','transport',' gasoline powered vehicles','gasoline');
CREATE TABLE "tech_reserve" (
	"tech"	text,
	"notes"	text,
	PRIMARY KEY("tech")
);
CREATE TABLE "tech_exchange" (
	"tech"	text,
	"notes"	text,
	PRIMARY KEY("tech")
);
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
INSERT INTO `regions` VALUES ('utopia',NULL);
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
	FOREIGN KEY("flag") REFERENCES "commodity_labels"("comm_labels"),
	PRIMARY KEY("comm_name")
);
INSERT INTO `commodities` VALUES ('ethos','p','# dummy commodity to supply inputs (makes graph easier to read)');
INSERT INTO `commodities` VALUES ('DSL','p','# diesel');
INSERT INTO `commodities` VALUES ('ELC','p','# electricity');
INSERT INTO `commodities` VALUES ('FEQ','p','# fossil equivalent');
INSERT INTO `commodities` VALUES ('GSL','p','# gasoline');
INSERT INTO `commodities` VALUES ('HCO','p','# coal');
INSERT INTO `commodities` VALUES ('HYD','p','# water');
INSERT INTO `commodities` VALUES ('OIL','p','# crude oil');
INSERT INTO `commodities` VALUES ('URN','p','# uranium');
INSERT INTO `commodities` VALUES ('co2','e','#CO2 emissions');
INSERT INTO `commodities` VALUES ('nox','e','#NOX emissions');
INSERT INTO `commodities` VALUES ('RH','d','# residential heating');
INSERT INTO `commodities` VALUES ('RL','d','# residential lighting');
INSERT INTO `commodities` VALUES ('TX','d','# transportation');
CREATE TABLE "TechOutputSplit" (
	"regions"	TEXT,
	"periods"	integer,
	"tech"	TEXT,
	"output_comm"	text,
	"to_split"	real,
	"to_split_notes"	text,
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","periods","tech","output_comm")
);
INSERT INTO `TechOutputSplit` VALUES ('utopia',1990,'SRE','DSL',0.7,'');
INSERT INTO `TechOutputSplit` VALUES ('utopia',2000,'SRE','DSL',0.7,'');
INSERT INTO `TechOutputSplit` VALUES ('utopia',2010,'SRE','DSL',0.7,'');
INSERT INTO `TechOutputSplit` VALUES ('utopia',1990,'SRE','GSL',0.3,'');
INSERT INTO `TechOutputSplit` VALUES ('utopia',2000,'SRE','GSL',0.3,'');
INSERT INTO `TechOutputSplit` VALUES ('utopia',2010,'SRE','GSL',0.3,'');
CREATE TABLE "TechInputSplit" (
	"regions"	TEXT,
	"periods"	integer,
	"input_comm"	text,
	"tech"	text,
	"ti_split"	real,
	"ti_split_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","periods","input_comm","tech")
);
CREATE TABLE "StorageDuration" (
	"regions"	text,
	"tech"	text,
	"duration"	real,
	"duration_notes"	text,
	PRIMARY KEY("regions","tech")
);
CREATE TABLE "SegFrac" (
	"season_name"	text,
	"time_of_day_name"	text,
	"segfrac"	real CHECK("segfrac" >= 0 AND "segfrac" <= 1),
	"segfrac_notes"	text,
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day"),
	PRIMARY KEY("season_name","time_of_day_name")
);
INSERT INTO `SegFrac` VALUES ('inter','day',0.1667,'# I-D');
INSERT INTO `SegFrac` VALUES ('inter','night',0.0833,'# I-N');
INSERT INTO `SegFrac` VALUES ('summer','day',0.1667,'# S-D');
INSERT INTO `SegFrac` VALUES ('summer','night',0.0833,'# S-N');
INSERT INTO `SegFrac` VALUES ('winter','day',0.3333,'# W-D');
INSERT INTO `SegFrac` VALUES ('winter','night',0.1667,'# W-N');
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
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	PRIMARY KEY("regions","scenario","tech","vintage")
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
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("t_season") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("t_day") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","scenario","t_periods","t_season","t_day","input_comm","tech","vintage","output_comm")
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
	FOREIGN KEY("t_season") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_day") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	PRIMARY KEY("regions","scenario","t_periods","t_season","t_day","input_comm","tech","vintage","output_comm")
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
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("emissions_comm") REFERENCES "EmissionActivity"("emis_comm"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","scenario","t_periods","emissions_comm","tech","vintage")
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
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("t_season") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_day") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","scenario","t_periods","t_season","t_day","input_comm","tech","vintage","output_comm")
);
CREATE TABLE "Output_Costs" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"output_name"	text,
	"tech"	text,
	"vintage"	integer,
	"output_cost"	real,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","scenario","output_name","tech","vintage")
);
CREATE TABLE "Output_CapacityByPeriodAndTech" (
	"regions"	text,
	"scenario"	text,
	"sector"	text,
	"t_periods"	integer,
	"tech"	text,
	"capacity"	real,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("t_periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("sector") REFERENCES "sector_labels"("sector"),
	PRIMARY KEY("regions","scenario","t_periods","tech")
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
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","periods","tech")
);
INSERT INTO `MinCapacity` VALUES ('utopia',1990,'E31',0.13,'','');
INSERT INTO `MinCapacity` VALUES ('utopia',2000,'E31',0.13,'','');
INSERT INTO `MinCapacity` VALUES ('utopia',2010,'E31',0.13,'','');
INSERT INTO `MinCapacity` VALUES ('utopia',1990,'SRE',0.1,'','');
CREATE TABLE "MinActivity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"minact"	real,
	"minact_units"	text,
	"minact_notes"	text,
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","periods","tech")
);
CREATE TABLE "MaxCapacity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"maxcap"	real,
	"maxcap_units"	text,
	"maxcap_notes"	text,
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","periods","tech")
);
INSERT INTO `MaxCapacity` VALUES ('utopia',1990,'E31',0.13,'','');
INSERT INTO `MaxCapacity` VALUES ('utopia',2000,'E31',0.17,'','');
INSERT INTO `MaxCapacity` VALUES ('utopia',2010,'E31',0.21,'','');
INSERT INTO `MaxCapacity` VALUES ('utopia',1990,'RHE',0.0,'','');
INSERT INTO `MaxCapacity` VALUES ('utopia',1990,'TXD',0.6,'','');
INSERT INTO `MaxCapacity` VALUES ('utopia',2000,'TXD',1.76,'','');
INSERT INTO `MaxCapacity` VALUES ('utopia',2010,'TXD',4.76,'','');
CREATE TABLE "MaxActivity" (
	"regions"	text,
	"periods"	integer,
	"tech"	text,
	"maxact"	real,
	"maxact_units"	text,
	"maxact_notes"	text,
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","periods","tech")
);
CREATE TABLE "LifetimeTech" (
	"regions"	text,
	"tech"	text,
	"life"	real,
	"life_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
);
INSERT INTO `LifetimeTech` VALUES ('utopia','E01',40.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','E21',40.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','E31',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','E51',100.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','E70',40.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','RHE',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','RHO',30.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','RL1',10.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','SRE',50.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','TXD',15.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','TXE',15.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','TXG',15.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPDSL1',1000.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPGSL1',1000.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPHCO1',1000.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPOIL1',1000.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPURN1',1000.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPHYD',1000.0,'');
INSERT INTO `LifetimeTech` VALUES ('utopia','IMPFEQ',1000.0,'');
CREATE TABLE "LifetimeProcess" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"life_process"	real,
	"life_process_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","tech","vintage")
);
INSERT INTO `LifetimeProcess` VALUES ('utopia','RL1',1980,20.0,'#forexistingcap');
INSERT INTO `LifetimeProcess` VALUES ('utopia','TXD',1970,30.0,'#forexistingcap');
INSERT INTO `LifetimeProcess` VALUES ('utopia','TXD',1980,30.0,'#forexistingcap');
INSERT INTO `LifetimeProcess` VALUES ('utopia','TXG',1970,30.0,'#forexistingcap');
INSERT INTO `LifetimeProcess` VALUES ('utopia','TXG',1980,30.0,'#forexistingcap');
CREATE TABLE "LifetimeLoanTech" (
	"regions"	text,
	"tech"	text,
	"loan"	real,
	"loan_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
);
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','E01',40.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','E21',40.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','E31',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','E51',100.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','E70',40.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','RHE',30.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','RHO',30.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','RL1',10.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','SRE',50.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','TXD',15.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','TXE',15.0,'');
INSERT INTO `LifetimeLoanTech` VALUES ('utopia','TXG',15.0,'');
CREATE TABLE "GrowthRateSeed" (
	"regions"	text,
	"tech"	text,
	"growthrate_seed"	real,
	"growthrate_seed_units"	text,
	"growthrate_seed_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
);
CREATE TABLE "GrowthRateMax" (
	"regions"	text,
	"tech"	text,
	"growthrate_max"	real,
	"growthrate_max_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
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
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech","vintage")
);
INSERT INTO `ExistingCapacity` VALUES ('utopia','E01',1960,0.175,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E01',1970,0.175,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E01',1980,0.15,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E31',1980,0.1,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E51',1980,0.5,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E70',1960,0.05,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E70',1970,0.05,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','E70',1980,0.2,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','RHO',1970,12.5,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','RHO',1980,12.5,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','RL1',1980,5.6,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','TXD',1970,0.4,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','TXD',1980,0.2,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','TXG',1970,3.1,'','');
INSERT INTO `ExistingCapacity` VALUES ('utopia','TXG',1980,1.5,'','');
CREATE TABLE "EmissionLimit" (
	"regions"	text,
	"periods"	integer,
	"emis_comm"	text,
	"emis_limit"	real,
	"emis_limit_units"	text,
	"emis_limit_notes"	text,
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("emis_comm") REFERENCES "commodities"("comm_name"),
	PRIMARY KEY("regions","periods","emis_comm")
);
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
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("emis_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	PRIMARY KEY("regions","emis_comm","input_comm","tech","vintage","output_comm")
);
INSERT INTO `EmissionActivity` VALUES ('utopia','co2','ethos','IMPDSL1',1990,'DSL',0.075,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','co2','ethos','IMPGSL1',1990,'GSL',0.075,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','co2','ethos','IMPHCO1',1990,'HCO',0.089,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','co2','ethos','IMPOIL1',1990,'OIL',0.075,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','DSL','TXD',1970,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','DSL','TXD',1980,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','DSL','TXD',1990,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','DSL','TXD',2000,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','DSL','TXD',2010,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','GSL','TXG',1970,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','GSL','TXG',1980,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','GSL','TXG',1990,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','GSL','TXG',2000,'TX',1.0,'','');
INSERT INTO `EmissionActivity` VALUES ('utopia','nox','GSL','TXG',2010,'TX',1.0,'','');
CREATE TABLE "Efficiency" (
	"regions"	text,
	"input_comm"	text,
	"tech"	text,
	"vintage"	integer,
	"output_comm"	text,
	"efficiency"	real CHECK("efficiency" > 0),
	"eff_notes"	text,
	FOREIGN KEY("input_comm") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("output_comm") REFERENCES "commodities"("comm_name"),
	PRIMARY KEY("regions","input_comm","tech","vintage","output_comm")
);
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPDSL1',1990,'DSL',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPGSL1',1990,'GSL',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPHCO1',1990,'HCO',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPOIL1',1990,'OIL',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPURN1',1990,'URN',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPFEQ',1990,'FEQ',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','ethos','IMPHYD',1990,'HYD',1.0,'');
INSERT INTO `Efficiency` VALUES ('utopia','HCO','E01',1960,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HCO','E01',1970,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HCO','E01',1980,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HCO','E01',1990,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HCO','E01',2000,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HCO','E01',2010,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','FEQ','E21',1990,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','FEQ','E21',2000,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','FEQ','E21',2010,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','URN','E21',1990,'ELC',0.4,'# 1/2.5');
INSERT INTO `Efficiency` VALUES ('utopia','URN','E21',2000,'ELC',0.4,'# 1/2.5');
INSERT INTO `Efficiency` VALUES ('utopia','URN','E21',2010,'ELC',0.4,'# 1/2.5');
INSERT INTO `Efficiency` VALUES ('utopia','HYD','E31',1980,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HYD','E31',1990,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HYD','E31',2000,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','HYD','E31',2010,'ELC',0.32,'# 1/3.125');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','E70',1960,'ELC',0.294,'# 1/3.4');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','E70',1970,'ELC',0.294,'# 1/3.4');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','E70',1980,'ELC',0.294,'# 1/3.4');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','E70',1990,'ELC',0.294,'# 1/3.4');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','E70',2000,'ELC',0.294,'# 1/3.4');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','E70',2010,'ELC',0.294,'# 1/3.4');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','E51',1980,'ELC',0.72,'# 1/1.3889');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','E51',1990,'ELC',0.72,'# 1/1.3889');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','E51',2000,'ELC',0.72,'# 1/1.3889');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','E51',2010,'ELC',0.72,'# 1/1.3889');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RHE',1990,'RH',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RHE',2000,'RH',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RHE',2010,'RH',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','RHO',1970,'RH',0.7,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','RHO',1980,'RH',0.7,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','RHO',1990,'RH',0.7,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','RHO',2000,'RH',0.7,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','RHO',2010,'RH',0.7,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RL1',1980,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RL1',1990,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RL1',2000,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','RL1',2010,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','OIL','SRE',1990,'DSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO `Efficiency` VALUES ('utopia','OIL','SRE',2000,'DSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO `Efficiency` VALUES ('utopia','OIL','SRE',2010,'DSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO `Efficiency` VALUES ('utopia','OIL','SRE',1990,'GSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO `Efficiency` VALUES ('utopia','OIL','SRE',2000,'GSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO `Efficiency` VALUES ('utopia','OIL','SRE',2010,'GSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','TXD',1970,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','TXD',1980,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','TXD',1990,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','TXD',2000,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','DSL','TXD',2010,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','TXE',1990,'TX',0.827,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','TXE',2000,'TX',0.827,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','ELC','TXE',2010,'TX',0.827,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','GSL','TXG',1970,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','GSL','TXG',1980,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','GSL','TXG',1990,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','GSL','TXG',2000,'TX',0.231,'# direct translation from DMD_EFF');
INSERT INTO `Efficiency` VALUES ('utopia','GSL','TXG',2010,'TX',0.231,'# direct translation from DMD_EFF');
CREATE TABLE "DiscountRate" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"tech_rate"	real,
	"tech_rate_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","tech","vintage")
);
CREATE TABLE "DemandSpecificDistribution" (
	"regions"	text,
	"season_name"	text,
	"time_of_day_name"	text,
	"demand_name"	text,
	"dds"	real CHECK("dds" >= 0 AND "dds" <= 1),
	"dds_notes"	text,
	FOREIGN KEY("demand_name") REFERENCES "commodities"("comm_name"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	PRIMARY KEY("regions","season_name","time_of_day_name","demand_name")
);
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','inter','day','RH',0.12,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','inter','night','RH',0.06,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','winter','day','RH',0.5467,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','winter','night','RH',0.2733,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','inter','day','RL',0.15,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','inter','night','RL',0.05,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','summer','day','RL',0.15,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','summer','night','RL',0.05,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','winter','day','RL',0.5,'');
INSERT INTO `DemandSpecificDistribution` VALUES ('utopia','winter','night','RL',0.1,'');
CREATE TABLE "Demand" (
	"regions"	text,
	"periods"	integer,
	"demand_comm"	text,
	"demand"	real,
	"demand_units"	text,
	"demand_notes"	text,
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("demand_comm") REFERENCES "commodities"("comm_name"),
	PRIMARY KEY("regions","periods","demand_comm")
);
INSERT INTO `Demand` VALUES ('utopia',1990,'RH',25.2,'','');
INSERT INTO `Demand` VALUES ('utopia',2000,'RH',37.8,'','');
INSERT INTO `Demand` VALUES ('utopia',2010,'RH',56.7,'','');
INSERT INTO `Demand` VALUES ('utopia',1990,'RL',5.6,'','');
INSERT INTO `Demand` VALUES ('utopia',2000,'RL',8.4,'','');
INSERT INTO `Demand` VALUES ('utopia',2010,'RL',12.6,'','');
INSERT INTO `Demand` VALUES ('utopia',1990,'TX',5.2,'','');
INSERT INTO `Demand` VALUES ('utopia',2000,'TX',7.8,'','');
INSERT INTO `Demand` VALUES ('utopia',2010,'TX',11.69,'','');
CREATE TABLE "CostVariable" (
	"regions"	text NOT NULL,
	"periods"	integer NOT NULL,
	"tech"	text NOT NULL,
	"vintage"	integer NOT NULL,
	"cost_variable"	real,
	"cost_variable_units"	text,
	"cost_variable_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","periods","tech","vintage")
);
INSERT INTO `CostVariable` VALUES ('utopia',1990,'IMPDSL1',1990,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'IMPDSL1',1990,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'IMPDSL1',1990,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'IMPGSL1',1990,15.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'IMPGSL1',1990,15.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'IMPGSL1',1990,15.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'IMPHCO1',1990,2.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'IMPHCO1',1990,2.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'IMPHCO1',1990,2.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'IMPOIL1',1990,8.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'IMPOIL1',1990,8.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'IMPOIL1',1990,8.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'IMPURN1',1990,2.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'IMPURN1',1990,2.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'IMPURN1',1990,2.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E01',1960,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E01',1970,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E01',1980,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E01',1990,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E01',1970,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E01',1980,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E01',1990,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E01',2000,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E01',1980,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E01',1990,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E01',2000,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E01',2010,0.3,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E21',1990,1.5,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E21',1990,1.5,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E21',1990,1.5,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E21',2000,1.5,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E21',2000,1.5,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E21',2010,1.5,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E70',1960,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E70',1970,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E70',1980,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'E70',1990,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E70',1970,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E70',1980,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E70',1990,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'E70',2000,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E70',1980,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E70',1990,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E70',2000,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'E70',2010,0.4,'','');
INSERT INTO `CostVariable` VALUES ('utopia',1990,'SRE',1990,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'SRE',1990,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2000,'SRE',2000,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'SRE',1990,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'SRE',2000,10.0,'','');
INSERT INTO `CostVariable` VALUES ('utopia',2010,'SRE',2010,10.0,'','');
CREATE TABLE "CostInvest" (
	"regions"	text,
	"tech"	text,
	"vintage"	integer,
	"cost_invest"	real,
	"cost_invest_units"	text,
	"cost_invest_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","tech","vintage")
);
INSERT INTO `CostInvest` VALUES ('utopia','E01',1990,2000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E01',2000,1300.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E01',2010,1200.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E21',1990,5000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E21',2000,5000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E21',2010,5000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E31',1990,3000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E31',2000,3000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E31',2010,3000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E51',1990,900.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E51',2000,900.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E51',2010,900.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E70',1990,1000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E70',2000,1000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','E70',2010,1000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','RHE',1990,90.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','RHE',2000,90.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','RHE',2010,90.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','RHO',1990,100.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','RHO',2000,100.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','RHO',2010,100.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','SRE',1990,100.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','SRE',2000,100.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','SRE',2010,100.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXD',1990,1044.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXD',2000,1044.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXD',2010,1044.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXE',1990,2000.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXE',2000,1750.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXE',2010,1500.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXG',1990,1044.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXG',2000,1044.0,'','');
INSERT INTO `CostInvest` VALUES ('utopia','TXG',2010,1044.0,'','');
CREATE TABLE "CostFixed" (
	"regions"	text NOT NULL,
	"periods"	integer NOT NULL,
	"tech"	text NOT NULL,
	"vintage"	integer NOT NULL,
	"cost_fixed"	real,
	"cost_fixed_units"	text,
	"cost_fixed_notes"	text,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("periods") REFERENCES "time_periods"("t_periods"),
	FOREIGN KEY("vintage") REFERENCES "time_periods"("t_periods"),
	PRIMARY KEY("regions","periods","tech","vintage")
);
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E01',1960,40.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E01',1970,40.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E01',1980,40.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E01',1990,40.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E01',1970,70.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E01',1980,70.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E01',1990,70.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E01',2000,70.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E01',1980,100.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E01',1990,100.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E01',2000,100.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E01',2010,100.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E21',1990,500.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E21',1990,500.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E21',1990,500.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E21',2000,500.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E21',2000,500.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E21',2010,500.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E31',1980,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E31',1990,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E31',1980,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E31',1990,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E31',2000,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E31',1980,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E31',1990,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E31',2000,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E31',2010,75.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E51',1980,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E51',1990,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E51',1980,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E51',1990,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E51',2000,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E51',1980,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E51',1990,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E51',2000,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E51',2010,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E70',1960,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E70',1970,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E70',1980,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'E70',1990,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E70',1970,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E70',1980,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E70',1990,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'E70',2000,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E70',1980,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E70',1990,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E70',2000,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'E70',2010,30.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'RHO',1970,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'RHO',1980,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'RHO',1990,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'RHO',1980,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'RHO',1990,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'RHO',2000,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'RHO',1990,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'RHO',2000,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'RHO',2010,1.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'RL1',1980,9.46,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'RL1',1990,9.46,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'RL1',2000,9.46,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'RL1',2010,9.46,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXD',1970,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXD',1980,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXD',1990,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXD',1980,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXD',1990,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXD',2000,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'TXD',2000,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'TXD',2010,52.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXE',1990,100.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXE',1990,90.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXE',2000,90.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'TXE',2000,80.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'TXE',2010,80.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXG',1970,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXG',1980,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',1990,'TXG',1990,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXG',1980,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXG',1990,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2000,'TXG',2000,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'TXG',2000,48.0,'','');
INSERT INTO `CostFixed` VALUES ('utopia',2010,'TXG',2010,48.0,'','');
CREATE TABLE "CapacityToActivity" (
	"regions"	text,
	"tech"	text,
	"c2a"	real,
	"c2a_notes"	TEXT,
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","tech")
);
INSERT INTO `CapacityToActivity` VALUES ('utopia','E01',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','E21',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','E31',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','E51',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','E70',31.54,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','RHE',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','RHO',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','RL1',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','SRE',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','TXD',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','TXE',1.0,'');
INSERT INTO `CapacityToActivity` VALUES ('utopia','TXG',1.0,'');
CREATE TABLE "CapacityFactorTech" (
	"regions"	text,
	"season_name"	text,
	"time_of_day_name"	text,
	"tech"	text,
	"cf_tech"	real CHECK("cf_tech" >= 0 AND "cf_tech" <= 1),
	"cf_tech_notes"	text,
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	PRIMARY KEY("regions","season_name","time_of_day_name","tech")
);
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','day','E01',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','night','E01',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','day','E01',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','night','E01',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','day','E01',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','night','E01',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','day','E21',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','night','E21',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','day','E21',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','night','E21',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','day','E21',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','night','E21',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','day','E31',0.275,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','night','E31',0.275,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','day','E31',0.275,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','night','E31',0.275,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','day','E31',0.275,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','night','E31',0.275,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','day','E51',0.17,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','night','E51',0.17,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','day','E51',0.17,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','night','E51',0.17,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','day','E51',0.17,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','night','E51',0.17,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','day','E70',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','inter','night','E70',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','day','E70',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','winter','night','E70',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','day','E70',0.8,'');
INSERT INTO `CapacityFactorTech` VALUES ('utopia','summer','night','E70',0.8,'');
CREATE TABLE "CapacityFactorProcess" (
	"regions"	text,
	"season_name"	text,
	"time_of_day_name"	text,
	"tech"	text,
	"vintage"	integer,
	"cf_process"	real CHECK("cf_process" >= 0 AND "cf_process" <= 1),
	"cf_process_notes"	text,
	FOREIGN KEY("season_name") REFERENCES "time_season"("t_season"),
	FOREIGN KEY("tech") REFERENCES "technologies"("tech"),
	FOREIGN KEY("time_of_day_name") REFERENCES "time_of_day"("t_day"),
	PRIMARY KEY("regions","season_name","time_of_day_name","tech","vintage")
);
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','inter','day','E31',2000,0.2753,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','inter','night','E31',2000,0.2753,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','winter','day','E31',2000,0.2753,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','winter','night','E31',2000,0.2753,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','summer','day','E31',2000,0.2753,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','summer','night','E31',2000,0.2753,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','inter','day','E31',2010,0.2756,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','inter','night','E31',2010,0.2756,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','winter','day','E31',2010,0.2756,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','winter','night','E31',2010,0.2756,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','summer','day','E31',2010,0.2756,'');
INSERT INTO `CapacityFactorProcess` VALUES ('utopia','summer','night','E31',2010,0.2756,'');
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
#INSERT INTO `MaxResource` VALUES ('utopia','IMPGSL1',60,'','');

COMMIT;
