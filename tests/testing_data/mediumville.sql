PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE metadata
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
INSERT INTO metadata VALUES('DB_MAJOR',3,'DB major version number');
INSERT INTO metadata VALUES('DB_MINOR',1,'DB minor version number');
INSERT INTO metadata VALUES ('days_per_period', 365, 'count of days in each period');
CREATE TABLE metadata_real
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO metadata_real VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in loan_rate table');
INSERT INTO metadata_real VALUES('global_discount_rate',0.42000000000000004,'');
CREATE TABLE output_dual_variable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
CREATE TABLE OutputObjective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
);
CREATE TABLE SeasonLabel
(
    season TEXT PRIMARY KEY,
    notes  TEXT
);
INSERT INTO SeasonLabel VALUES('s1',NULL);
INSERT INTO SeasonLabel VALUES('s2',NULL);
CREATE TABLE SectorLabel
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
INSERT INTO SectorLabel VALUES('supply',NULL);
INSERT INTO SectorLabel VALUES('electric',NULL);
INSERT INTO SectorLabel VALUES('transport',NULL);
INSERT INTO SectorLabel VALUES('commercial',NULL);
INSERT INTO SectorLabel VALUES('residential',NULL);
INSERT INTO SectorLabel VALUES('industrial',NULL);
CREATE TABLE capacity_credit
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    tech    TEXT
        REFERENCES technology (tech),
    vintage INTEGER,
    credit  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage),
    CHECK (credit >= 0 AND credit <= 1)
);
INSERT INTO capacity_credit VALUES('A',2025,'EF',2025,0.5999999999999999778,NULL);
CREATE TABLE capacity_factor_process
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    tech    TEXT
        REFERENCES technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, season, tod, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO capacity_factor_process VALUES('A',2025,'s2','d1','EFL',2025,0.8000000000000000444,NULL);
INSERT INTO capacity_factor_process VALUES('A',2025,'s1','d2','EFL',2025,0.9000000000000000222,NULL);
CREATE TABLE capacity_factor_tech
(
    region TEXT,
    period INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod    TEXT
        REFERENCES TimeOfDay (tod),
    tech   TEXT
        REFERENCES technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, period, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO capacity_factor_tech VALUES('A',2025,'s1','d1','EF',0.8000000000000000444,NULL);
INSERT INTO capacity_factor_tech VALUES('B',2025,'s2','d2','bulbs',0.75,NULL);
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('A','bulbs',1.0,'');
INSERT INTO CapacityToActivity VALUES('B','bulbs',1.0,NULL);
CREATE TABLE commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES commodityType (label),
    description TEXT
);
INSERT INTO commodity VALUES('ELC','p','electricity');
INSERT INTO commodity VALUES('HYD','p','water');
INSERT INTO commodity VALUES('co2','e','CO2 emissions');
INSERT INTO commodity VALUES('RL','d','residential lighting');
INSERT INTO commodity VALUES('earth','s','the source of stuff');
INSERT INTO commodity VALUES('RH','d','residential heat');
INSERT INTO commodity VALUES('FusionGas','e','mystery emission');
INSERT INTO commodity VALUES('FusionGasFuel','p','converted mystery gas to fuel');
INSERT INTO commodity VALUES('GeoHyd','p','Hot water from geo');
CREATE TABLE commodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO commodityType VALUES('w','waste commodity');
INSERT INTO commodityType VALUES('wa','waste annual commodity');
INSERT INTO commodityType VALUES('wp','waste physical commodity');
INSERT INTO commodityType VALUES('a','annual commodity');
INSERT INTO commodityType VALUES('p','physical commodity');
INSERT INTO commodityType VALUES('e','emissions commodity');
INSERT INTO commodityType VALUES('d','demand commodity');
INSERT INTO commodityType VALUES('s','source commodity');
CREATE TABLE construction_input
(
    region      TEXT,
    input_comm   TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage)
);
CREATE TABLE cost_emission
(
    region    TEXT,
    period    INTEGER
        REFERENCES time_period (period),
    emis_comm TEXT NOT NULL
        REFERENCES commodity (name),
    cost      REAL NOT NULL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm)
);
INSERT INTO cost_emission VALUES('A',2025,'co2',1.989999999999999992,'dollars','none');
CREATE TABLE cost_fixed
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL
        REFERENCES time_period (period),
    tech    TEXT    NOT NULL
        REFERENCES technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES time_period (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
INSERT INTO cost_fixed VALUES('A',2025,'EH',2025,3.299999999999999823,'','');
INSERT INTO cost_fixed VALUES('A',2025,'EF',2025,2.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('A',2025,'EFL',2025,3.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'batt',2025,1.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'EF',2025,2.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('A',2025,'bulbs',2025,1.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'bulbs',2025,1.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('A',2025,'heater',2025,2.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'heater',2025,2.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'GeoThermal',2025,6.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'GeoHeater',2025,1.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('B',2025,'EH',2025,3.299999999999999823,NULL,NULL);
INSERT INTO cost_fixed VALUES('A',2025,'GeoThermal',2025,4.0,NULL,NULL);
INSERT INTO cost_fixed VALUES('A',2025,'GeoHeater',2025,4.5,NULL,NULL);
CREATE TABLE cost_invest
(
    region  TEXT,
    tech    TEXT
        REFERENCES technology (tech),
    vintage INTEGER
        REFERENCES time_period (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech, vintage)
);
INSERT INTO cost_invest VALUES('A','EF',2025,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('A','EH',2025,3.0,NULL,NULL);
INSERT INTO cost_invest VALUES('A','bulbs',2025,4.0,NULL,NULL);
INSERT INTO cost_invest VALUES('A','heater',2025,5.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','EF',2025,6.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','batt',2025,7.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','bulbs',2025,8.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','heater',2025,9.0,NULL,NULL);
INSERT INTO cost_invest VALUES('A','EFL',2025,2.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','GeoThermal',2025,3.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','GeoHeater',2025,4.0,NULL,NULL);
INSERT INTO cost_invest VALUES('B','EH',2025,3.299999999999999823,NULL,NULL);
INSERT INTO cost_invest VALUES('A','GeoThermal',2025,5.599999999999999645,NULL,NULL);
INSERT INTO cost_invest VALUES('A','GeoHeater',2025,4.200000000000000177,NULL,NULL);
CREATE TABLE cost_variable
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL
        REFERENCES time_period (period),
    tech    TEXT    NOT NULL
        REFERENCES technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES time_period (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
INSERT INTO cost_variable VALUES('A',2025,'EF',2025,9.0,NULL,NULL);
INSERT INTO cost_variable VALUES('A',2025,'EFL',2025,8.0,NULL,NULL);
INSERT INTO cost_variable VALUES('A',2025,'EH',2025,7.0,NULL,NULL);
INSERT INTO cost_variable VALUES('A',2025,'bulbs',2025,6.0,NULL,NULL);
INSERT INTO cost_variable VALUES('A',2025,'heater',2025,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('B',2025,'EF',2025,4.0,NULL,NULL);
INSERT INTO cost_variable VALUES('B',2025,'batt',2025,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('B',2025,'bulbs',2025,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('B',2025,'heater',2025,1.0,NULL,NULL);
CREATE TABLE demand
(
    region    TEXT,
    period    INTEGER
        REFERENCES time_period (period),
    commodity TEXT
        REFERENCES commodity (name),
    demand    REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, commodity)
);
INSERT INTO demand VALUES('A',2025,'RL',100.0,'','');
INSERT INTO demand VALUES('B',2025,'RL',100.0,NULL,NULL);
INSERT INTO demand VALUES('A',2025,'RH',50.0,NULL,NULL);
INSERT INTO demand VALUES('B',2025,'RH',50.0,NULL,NULL);
CREATE TABLE demand_specific_distribution
(
    region      TEXT,
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES commodity (name),
    dsd         REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s1','d1','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s1','d2','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s2','d1','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s2','d2','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s1','d1','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s1','d2','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s2','d1','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s2','d2','RL',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s1','d1','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s2','d1','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s1','d1','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s2','d1','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s1','d2','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('A',2025,'s2','d2','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s1','d2','RH',0.25,NULL);
INSERT INTO demand_specific_distribution VALUES('B',2025,'s2','d2','RH',0.25,NULL);
CREATE TABLE end_of_life_output
(
    region      TEXT,
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm   TEXT
        REFERENCES commodity (name),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, tech, vintage, output_comm)
);
CREATE TABLE efficiency
(
    region      TEXT,
    input_comm  TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm TEXT
        REFERENCES commodity (name),
    efficiency  REAL,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
INSERT INTO efficiency VALUES('A','ELC','bulbs',2025,'RL',1.0,NULL);
INSERT INTO efficiency VALUES('A','HYD','EH',2025,'ELC',1.0,NULL);
INSERT INTO efficiency VALUES('A','HYD','EF',2025,'ELC',1.0,NULL);
INSERT INTO efficiency VALUES('B','ELC','bulbs',2025,'RL',1.0,NULL);
INSERT INTO efficiency VALUES('B','HYD','EH',2025,'ELC',1.0,NULL);
INSERT INTO efficiency VALUES('B','ELC','batt',2025,'ELC',1.0,NULL);
INSERT INTO efficiency VALUES('B','HYD','EF',2025,'ELC',1.0,NULL);
INSERT INTO efficiency VALUES('A','earth','well',2025,'HYD',1.0,NULL);
INSERT INTO efficiency VALUES('B','earth','well',2025,'HYD',1.0,NULL);
INSERT INTO efficiency VALUES('A','earth','EFL',2025,'FusionGasFuel',1.0,NULL);
INSERT INTO efficiency VALUES('A','FusionGasFuel','heater',2025,'RH',0.9000000000000000222,NULL);
INSERT INTO efficiency VALUES('A-B','FusionGasFuel','FGF_pipe',2025,'FusionGasFuel',0.949999999999999956,NULL);
INSERT INTO efficiency VALUES('B','FusionGasFuel','heater',2025,'RH',0.9000000000000000222,NULL);
INSERT INTO efficiency VALUES('B','GeoHyd','GeoHeater',2025,'RH',0.980000000000000094,NULL);
INSERT INTO efficiency VALUES('B','earth','GeoThermal',2025,'GeoHyd',1.0,NULL);
INSERT INTO efficiency VALUES('B-A','FusionGasFuel','FGF_pipe',2025,'FusionGasFuel',0.949999999999999956,NULL);
INSERT INTO efficiency VALUES('A','GeoHyd','GeoHeater',2025,'RH',0.9000000000000000222,NULL);
INSERT INTO efficiency VALUES('A','earth','GeoThermal',2025,'GeoHyd',1.0,NULL);
CREATE TABLE efficiency_variable
(
    region      TEXT,
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm TEXT
        REFERENCES commodity (name),
    efficiency  REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
CREATE TABLE emission_activity
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES commodity (name),
    input_comm  TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm TEXT
        REFERENCES commodity (name),
    activity    REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm, input_comm, tech, vintage, output_comm)
);
INSERT INTO emission_activity VALUES('A','co2','HYD','EH',2025,'ELC',0.02000000000000000041,NULL,NULL);
INSERT INTO emission_activity VALUES('A','FusionGas','HYD','EF',2025,'ELC',-0.2000000000000000111,NULL,'needs to be negative as a driver of linked tech...don''t ask');
CREATE TABLE emission_embodied
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm,  tech, vintage)
);
CREATE TABLE emission_end_of_life
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm,  tech, vintage)
);
CREATE TABLE existing_capacity
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    capacity REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
INSERT INTO existing_capacity VALUES('A','EH',2020,200.0,'things',NULL);
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
INSERT INTO TechGroup VALUES('RPS_common','');
INSERT INTO TechGroup VALUES('A_tech_grp_1','converted from old db');
CREATE TABLE loan_lifetime_process
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
INSERT INTO loan_lifetime_process VALUES('A','EF',2025,57,NULL);
INSERT INTO loan_lifetime_process VALUES('A','EFL',2025,68,NULL);
INSERT INTO loan_lifetime_process VALUES('A','bulbs',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('A','EH',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('A','well',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('A','heater',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('A','GeoHeater',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('A','GeoThermal',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','EF',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','bulbs',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','EH',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','batt',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','well',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','heater',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','GeoHeater',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B','GeoThermal',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('A-B','FGF_pipe',2025,10,NULL);
INSERT INTO loan_lifetime_process VALUES('B-A','FGF_pipe',2025,10,NULL);
CREATE TABLE loan_rate
(
    region  TEXT,
    tech    TEXT
        REFERENCES technology (tech),
    vintage INTEGER
        REFERENCES time_period (period),
    rate    REAL,
    notes   TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE lifetime_process
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
INSERT INTO lifetime_process VALUES('B','EF',2025,200.0,NULL);
CREATE TABLE lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO lifetime_tech VALUES('A','EH',60.0,'');
INSERT INTO lifetime_tech VALUES('B','bulbs',100.0,'super LED!');
CREATE TABLE Operator
(
	operator TEXT PRIMARY KEY,
	notes TEXT
);
INSERT INTO Operator VALUES('e','equal to');
INSERT INTO Operator VALUES('le','less than or equal to');
INSERT INTO Operator VALUES('ge','greater than or equal to');
CREATE TABLE limit_growth_capacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_degrowth_capacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_growth_new_capacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_degrowth_new_capacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_growth_new_capacity_delta
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_degrowth_new_capacity_delta
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitStorageLevelFraction
(
    region   TEXT,
    period   INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod      TEXT
        REFERENCES TimeOfDay (tod),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    fraction REAL,
    notes    TEXT,
    PRIMARY KEY(region, period, season, tod, tech, vintage, operator)
);
CREATE TABLE limit_activity
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    activity REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
INSERT INTO limit_activity VALUES('A',2025,'EF','ge',0.00100000000000000002,'PJ/CY','goofy units');
INSERT INTO limit_activity VALUES('B',2025,'EH','le',10000.0,'stuff',NULL);
INSERT INTO limit_activity VALUES('A',2025,'EF','le',10000.0,'stuff',NULL);
INSERT INTO limit_activity VALUES('A',2025,'A_tech_grp_1','ge',0.05000000000000000277,'',NULL);
INSERT INTO limit_activity VALUES('A',2025,'A_tech_grp_1','le',10000.0,'',NULL);
CREATE TABLE limit_activity_share
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE limit_annual_capacity_factor
(
    region      TEXT,
    period      INTEGER
        REFERENCES time_period (period),
    tech        TEXT
        REFERENCES technology (tech),
    output_comm TEXT
        REFERENCES commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    factor      REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE limit_capacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    capacity REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
INSERT INTO limit_capacity VALUES('A',2025,'EH','ge',0.1000000000000000055,'','');
INSERT INTO limit_capacity VALUES('B',2025,'batt','ge',0.1000000000000000055,'','');
INSERT INTO limit_capacity VALUES('A',2025,'EH','le',20000.0,'','');
INSERT INTO limit_capacity VALUES('B',2025,'EH','le',20000.0,'','');
INSERT INTO limit_capacity VALUES('A',2025,'A_tech_grp_1','ge',0.2000000000000000111,'',NULL);
INSERT INTO limit_capacity VALUES('A',2025,'A_tech_grp_1','le',6000.0,'',NULL);
CREATE TABLE limit_capacity_share
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE limit_new_capacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    new_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE limit_new_capacity_share
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
INSERT INTO limit_new_capacity_share VALUES('A',2025,'RPS_common','A_tech_grp_1','ge',0.0,'');
INSERT INTO limit_new_capacity_share VALUES('global',2025,'RPS_common','A_tech_grp_1','le',1.0,'');
CREATE TABLE limit_resource
(
    region  TEXT,
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    cum_act REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
INSERT INTO limit_resource VALUES('B','EF','le',9000.0,'clumps',NULL);
CREATE TABLE limit_seasonal_capacity_factor
(
	region  TEXT
        REFERENCES region (region),
	period	INTEGER
        REFERENCES time_period (period),
	season TEXT
        REFERENCES SeasonLabel (season),
	tech    TEXT
        REFERENCES technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
	factor	REAL,
	notes	TEXT,
	PRIMARY KEY(region, period, season, tech, operator)
);
CREATE TABLE limit_tech_input_split
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    input_comm     TEXT
        REFERENCES commodity (name),
    tech           TEXT
        REFERENCES technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
INSERT INTO limit_tech_input_split VALUES('A',2025,'HYD','EH','ge',0.949999999999999956,'95% HYD reqt.  (other not specified...)');
CREATE TABLE limit_tech_input_split_annual
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    input_comm     TEXT
        REFERENCES commodity (name),
    tech           TEXT
        REFERENCES technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
CREATE TABLE limit_tech_output_split
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    tech           TEXT
        REFERENCES technology (tech),
    output_comm    TEXT
        REFERENCES commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
INSERT INTO limit_tech_output_split VALUES('B',2025,'EH','ELC','ge',0.949999999999999956,'95% ELC output (there are not others, this is a min)');
CREATE TABLE limit_tech_output_split_annual
(
    region         TEXT,
    period         INTEGER
        REFERENCES time_period (period),
    tech           TEXT
        REFERENCES technology (tech),
    output_comm    TEXT
        REFERENCES commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
CREATE TABLE limit_emission
(
    region    TEXT,
    period    INTEGER
        REFERENCES time_period (period),
    emis_comm TEXT
        REFERENCES commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    value     REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm, operator)
);
INSERT INTO limit_emission VALUES('A',2025,'co2','le',10000.0,'gulps',NULL);
CREATE TABLE LinkedTech
(
    primary_region TEXT,
    primary_tech   TEXT
        REFERENCES technology (tech),
    emis_comm      TEXT
        REFERENCES commodity (name),
    driven_tech    TEXT
        REFERENCES technology (tech),
    notes          TEXT,
    PRIMARY KEY (primary_region, primary_tech, emis_comm)
);
INSERT INTO LinkedTech VALUES('A','EF','FusionGas','EFL',NULL);
CREATE TABLE output_curtailment
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT,
    period      INTEGER
        REFERENCES time_period (period),
    season      TEXT
        REFERENCES time_period (period),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm TEXT
        REFERENCES commodity (name),
    curtailment REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE OutputNetCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    period   INTEGER
        REFERENCES time_period (period),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE output_built_capacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, tech, vintage)
);
CREATE TABLE OutputRetiredCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    period   INTEGER
        REFERENCES time_period (period),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    cap_eol REAL,
    cap_early REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE OutputFlowIn
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm TEXT
        REFERENCES commodity (name),
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE OutputFlowOut
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES commodity (name),
    tech        TEXT
        REFERENCES technology (tech),
    vintage     INTEGER
        REFERENCES time_period (period),
    output_comm TEXT
        REFERENCES commodity (name),
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE output_storage_level
(
    scenario TEXT,
    region TEXT,
    sector TEXT
        REFERENCES SectorLabel (sector),
    period INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod TEXT
        REFERENCES TimeOfDay (tod),
    tech TEXT
        REFERENCES technology (tech),
    vintage INTEGER
        REFERENCES time_period (period),
    level REAL,
    PRIMARY KEY (scenario, region, period, season, tod, tech, vintage)
);
CREATE TABLE planning_reserve_margin
(
    region TEXT
        PRIMARY KEY
        REFERENCES region (region),
    margin REAL,
    notes TEXT
);
INSERT INTO planning_reserve_margin VALUES('A',0.05000000000000000277,NULL);
CREATE TABLE ramp_down_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO ramp_down_hourly VALUES('A','EH',0.05000000000000000277,NULL);
INSERT INTO ramp_down_hourly VALUES('B','EH',0.05000000000000000277,NULL);
CREATE TABLE ramp_up_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO ramp_up_hourly VALUES('B','EH',0.05000000000000000277,NULL);
INSERT INTO ramp_up_hourly VALUES('A','EH',0.05000000000000000277,NULL);
CREATE TABLE region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
INSERT INTO region VALUES('A','main region');
INSERT INTO region VALUES('B','just a 2nd region');
CREATE TABLE reserve_capacity_derate
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    season  TEXT
    	REFERENCES SeasonLabel (season),
    tech    TEXT
        REFERENCES technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, season, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE TimeSegmentFraction
(
    period INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    segfrac REAL,
    notes   TEXT,
    PRIMARY KEY (period, season, tod),
    CHECK (segfrac >= 0 AND segfrac <= 1)
);
INSERT INTO TimeSegmentFraction VALUES(2025,'s2','d1',0.25,NULL);
INSERT INTO TimeSegmentFraction VALUES(2025,'s2','d2',0.25,NULL);
INSERT INTO TimeSegmentFraction VALUES(2025,'s1','d1',0.25,NULL);
INSERT INTO TimeSegmentFraction VALUES(2025,'s1','d2',0.25,NULL);
CREATE TABLE storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO storage_duration VALUES('B','batt',15.0,NULL);
CREATE TABLE lifetime_survival_curve
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL,
    tech    TEXT    NOT NULL
        REFERENCES technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES time_period (period),
    fraction  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
CREATE TABLE technologyType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO technologyType VALUES('p','production technology');
INSERT INTO technologyType VALUES('pb','baseload production technology');
INSERT INTO technologyType VALUES('ps','storage production technology');
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(1,'d1');
INSERT INTO TimeOfDay VALUES(2,'d2');
CREATE TABLE time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_periodType (label)
);
INSERT INTO time_period VALUES(1,2020,'e');
INSERT INTO time_period VALUES(2,2025,'f');
INSERT INTO time_period VALUES(3,2030,'f');
CREATE TABLE TimeSeason
(
    period INTEGER
        REFERENCES time_period (period),
    sequence INTEGER,
    season TEXT
        REFERENCES SeasonLabel (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
INSERT INTO TimeSeason VALUES(2025,1,'s1',NULL);
INSERT INTO TimeSeason VALUES(2025,2,'s2',NULL);
CREATE TABLE time_season_sequential
(
    period INTEGER
        REFERENCES time_period (period),
    sequence INTEGER,
    seas_seq TEXT,
    season TEXT
        REFERENCES SeasonLabel (season),
    num_days REAL NOT NULL,
    notes TEXT,
    PRIMARY KEY (period, sequence, seas_seq, season),
    CHECK (num_days > 0)
);
CREATE TABLE time_periodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO time_periodType VALUES('e','existing vintages');
INSERT INTO time_periodType VALUES('f','future');
CREATE TABLE OutputEmission
(
    scenario  TEXT,
    region    TEXT,
    sector    TEXT
        REFERENCES SectorLabel (sector),
    period    INTEGER
        REFERENCES time_period (period),
    emis_comm TEXT
        REFERENCES commodity (name),
    tech      TEXT
        REFERENCES technology (tech),
    vintage   INTEGER
        REFERENCES time_period (period),
    emission  REAL,
    PRIMARY KEY (region, scenario, period, emis_comm, tech, vintage)
);
CREATE TABLE RPSRequirement
(
    region      TEXT    NOT NULL
        REFERENCES region (region),
    period      INTEGER NOT NULL
        REFERENCES time_period (period),
    tech_group  TEXT    NOT NULL
        REFERENCES TechGroup (group_name),
    requirement REAL    NOT NULL,
    notes       TEXT
);
INSERT INTO RPSRequirement VALUES('B',2025,'RPS_common',0.2999999999999999889,NULL);
CREATE TABLE TechGroupMember
(
    group_name TEXT
        REFERENCES TechGroup (group_name),
    tech       TEXT
        REFERENCES technology (tech),
    PRIMARY KEY (group_name, tech)
);
INSERT INTO TechGroupMember VALUES('RPS_common','EF');
INSERT INTO TechGroupMember VALUES('A_tech_grp_1','EH');
INSERT INTO TechGroupMember VALUES('A_tech_grp_1','EF');
CREATE TABLE technology
(
    tech         TEXT    NOT NULL PRIMARY KEY,
    flag         TEXT    NOT NULL,
    sector       TEXT,
    category     TEXT,
    sub_category TEXT,
    unlim_cap    INTEGER NOT NULL DEFAULT 0,
    annual       INTEGER NOT NULL DEFAULT 0,
    reserve      INTEGER NOT NULL DEFAULT 0,
    curtail      INTEGER NOT NULL DEFAULT 0,
    retire       INTEGER NOT NULL DEFAULT 0,
    flex         INTEGER NOT NULL DEFAULT 0,
    exchange     INTEGER NOT NULL DEFAULT 0,
    seas_stor    INTEGER NOT NULL DEFAULT 0,
    description  TEXT,
    FOREIGN KEY (flag) REFERENCES technologyType (label)
);
INSERT INTO technology VALUES('well','p','supply','water','',0,0,0,0,0,0,0,0,'plain old water');
INSERT INTO technology VALUES('bulbs','p','residential','electric','',0,0,0,0,0,0,0,0,'residential lighting');
INSERT INTO technology VALUES('EH','pb','electric','hydro','',0,0,0,1,1,0,0,0,'hydro power electric plant');
INSERT INTO technology VALUES('batt','ps','electric','electric','',0,0,0,0,0,0,0,0,'big battery');
INSERT INTO technology VALUES('EF','p','electric','electric','',0,0,1,0,0,0,0,0,'fusion plant');
INSERT INTO technology VALUES('EFL','p','electric','electric','',0,0,0,0,0,1,0,0,'linked (to Fusion) producer');
INSERT INTO technology VALUES('heater','p','residential','electric','',0,0,0,0,0,0,0,0,'heater');
INSERT INTO technology VALUES('FGF_pipe','p','transport',NULL,'',0,0,0,0,0,0,1,0,'transportation line A->B');
INSERT INTO technology VALUES('GeoThermal','p','residential','hydro','',0,1,0,0,0,0,0,0,'geothermal hot water source');
INSERT INTO technology VALUES('GeoHeater','p','residential','hydro','',0,0,0,0,0,0,0,0,'geothermal heater from geo hyd');
CREATE TABLE output_cost
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT REFERENCES SectorLabel (sector),
    period   INTEGER REFERENCES time_period (period),
    tech     TEXT REFERENCES technology (tech),
    vintage  INTEGER REFERENCES time_period (period),
    d_invest REAL,
    d_fixed  REAL,
    d_var    REAL,
    d_emiss  REAL,
    invest   REAL,
    fixed    REAL,
    var      REAL,
    emiss    REAL,
    PRIMARY KEY (scenario, region, period, tech, vintage),
    FOREIGN KEY (vintage) REFERENCES time_period (period),
    FOREIGN KEY (tech) REFERENCES technology (tech)
);
COMMIT;
