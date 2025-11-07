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
INSERT INTO metadata VALUES('days_per_period',365,'count of days in each period');
CREATE TABLE metadata_real
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO metadata_real VALUES('global_discount_rate',0.05,'Discount Rate for future costs');
INSERT INTO metadata_real VALUES('default_loan_rate',0.05,'Default Loan Rate if not specified in loan_rate table');
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
INSERT INTO SeasonLabel VALUES('charge','non-sequential season - charging day');
INSERT INTO SeasonLabel VALUES('discharge','non-sequential season - discharging day');
INSERT INTO SeasonLabel VALUES('summer','sequential season - summer day');
INSERT INTO SeasonLabel VALUES('sept_w1','sequential season - day in first week of September');
INSERT INTO SeasonLabel VALUES('sept_w2','sequential season - day in second week of September');
INSERT INTO SeasonLabel VALUES('sept_w3','sequential season - day in third week of September');
INSERT INTO SeasonLabel VALUES('sept_w4','sequential season - day in fourth week of September');
INSERT INTO SeasonLabel VALUES('sept_29th','sequential season - 29th of September');
INSERT INTO SeasonLabel VALUES('sept_30th','sequential season - 30th of September');
INSERT INTO SeasonLabel VALUES('winter','sequential season - winter day');
INSERT INTO SeasonLabel VALUES('apr_w1','sequential season - day in first week of September');
INSERT INTO SeasonLabel VALUES('apr_w2','sequential season - day in second week of September');
INSERT INTO SeasonLabel VALUES('apr_w3','sequential season - day in third week of September');
INSERT INTO SeasonLabel VALUES('apr_w4','sequential season - day in fourth week of September');
INSERT INTO SeasonLabel VALUES('apr_29th','sequential season - 29th of April');
INSERT INTO SeasonLabel VALUES('apr_30th','sequential season - 30th of April');
CREATE TABLE SectorLabel
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
INSERT INTO SectorLabel VALUES('electricity',NULL);
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
INSERT INTO capacity_factor_tech VALUES('region',2000,'charge','a','generator',1.0,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'charge','b','generator',1.0,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'charge','c','generator',0.2,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'charge','d','generator',0.2,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'discharge','a','generator',0.1,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'discharge','b','generator',0.1,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'discharge','c','generator',0.01,NULL);
INSERT INTO capacity_factor_tech VALUES('region',2000,'discharge','d','generator',0.01,NULL);
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('region','generator',8760.0,'MWh/MWy');
INSERT INTO CapacityToActivity VALUES('region','dly_stor',8760.0,'MWh/MWy');
INSERT INTO CapacityToActivity VALUES('region','seas_stor',8760.0,'MWh/MWy');
INSERT INTO CapacityToActivity VALUES('region','demand',8760.0,'MWh/MWy');
CREATE TABLE commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES commodityType (label),
    description TEXT
);
INSERT INTO commodity VALUES('ethos','s',NULL);
INSERT INTO commodity VALUES('electricity','p',NULL);
INSERT INTO commodity VALUES('demand','d',NULL);
CREATE TABLE commodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO commodityType VALUES('p','physical commodity');
INSERT INTO commodityType VALUES('a','annual commodity');
INSERT INTO commodityType VALUES('e','emissions commodity');
INSERT INTO commodityType VALUES('d','demand commodity');
INSERT INTO commodityType VALUES('s','source commodity');
INSERT INTO commodityType VALUES('w','waste commodity');
INSERT INTO commodityType VALUES('wa','waste annual commodity');
INSERT INTO commodityType VALUES('wp','waste physical commodity');
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
INSERT INTO cost_invest VALUES('region','generator',2000,1000.0,'',NULL);
INSERT INTO cost_invest VALUES('region','dly_stor',2000,1.0,'',NULL);
INSERT INTO cost_invest VALUES('region','seas_stor',2000,100.0,'',NULL);
INSERT INTO cost_invest VALUES('region','demand',2000,1.0,'',NULL);
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
INSERT INTO cost_variable VALUES('region',2000,'generator',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('region',2000,'demand',2000,1.0,NULL,NULL);
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
INSERT INTO demand VALUES('region',2000,'demand',8760.0,'MWh',NULL);
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
INSERT INTO demand_specific_distribution VALUES('region',2000,'charge','a','demand',0.0,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'charge','b','demand',0.05,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'charge','c','demand',0.05,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'charge','d','demand',0.1,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'discharge','a','demand',0.0,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'discharge','b','demand',0.2,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'discharge','c','demand',0.2,NULL);
INSERT INTO demand_specific_distribution VALUES('region',2000,'discharge','d','demand',0.4,NULL);
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
INSERT INTO efficiency VALUES('region','ethos','generator',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('region','electricity','dly_stor',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('region','electricity','seas_stor',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('region','electricity','demand',2000,'demand',1.0,NULL);
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
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
CREATE TABLE Loanlifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
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
CREATE TABLE lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
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
INSERT INTO LimitStorageLevelFraction VALUES('region', 2000, 'winter', 'b', 'seas_stor', 2000, 'e', 0.5, NULL);
INSERT INTO LimitStorageLevelFraction VALUES('region', 2000, 'charge', 'b', 'dly_stor', 2000, 'e', 0.5, NULL);
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
CREATE TABLE ramp_down_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE ramp_up_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
INSERT INTO region VALUES('region',NULL);
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
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','a',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','b',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','c',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','d',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','a',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','b',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','c',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','d',0.125,NULL);
CREATE TABLE storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO storage_duration VALUES('region','dly_stor',4.0,NULL);
INSERT INTO storage_duration VALUES('region','seas_stor',8760.0,NULL);
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
INSERT INTO TimeOfDay VALUES(0,'a');
INSERT INTO TimeOfDay VALUES(1,'b');
INSERT INTO TimeOfDay VALUES(2,'c');
INSERT INTO TimeOfDay VALUES(3,'d');
CREATE TABLE time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_periodType (label)
);
INSERT INTO time_period VALUES(0,2000,'f');
INSERT INTO time_period VALUES(1,2005,'f');
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
INSERT INTO TimeSeason VALUES(2000,0,'charge',NULL);
INSERT INTO TimeSeason VALUES(2000,1,'discharge',NULL);
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
CREATE TABLE TechGroupMember
(
    group_name TEXT
        REFERENCES TechGroup (group_name),
    tech       TEXT
        REFERENCES technology (tech),
    PRIMARY KEY (group_name, tech)
);
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
INSERT INTO technology VALUES('generator','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO technology VALUES('dly_stor','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO technology VALUES('seas_stor','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,1,NULL);
INSERT INTO technology VALUES('demand','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
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
INSERT INTO time_season_sequential VALUES(2000,1,'summer','charge',152.5,NULL);
INSERT INTO time_season_sequential VALUES(2000,2,'sept_w1','discharge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,3,'sept_w2','charge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,4,'sept_w3','discharge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,5,'sept_w4','charge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,6,'sept_29th','discharge',1,NULL);
INSERT INTO time_season_sequential VALUES(2000,7,'sept_30th','charge',1,NULL);
INSERT INTO time_season_sequential VALUES(2000,8,'winter','discharge',152.5,NULL);
INSERT INTO time_season_sequential VALUES(2000,9,'apr_w1','charge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,10,'apr_w2','discharge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,11,'apr_w3','charge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,12,'apr_w4','discharge',7,NULL);
INSERT INTO time_season_sequential VALUES(2000,13,'apr_29th','charge',1,NULL);
INSERT INTO time_season_sequential VALUES(2000,14,'apr_30th','discharge',1,NULL);
COMMIT;
