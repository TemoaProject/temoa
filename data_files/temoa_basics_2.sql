PRAGMA foreign_keys= OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS MetaData
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
REPLACE INTO MetaData
VALUES ('DB_MAJOR', 3, 'DB major version number');
REPLACE INTO MetaData
VALUES ('DB_MINOR', 1, 'DB minor version number');
REPLACE INTO MetaData
VALUES ('days_per_period', 365, 'count of days in each period');
CREATE TABLE IF NOT EXISTS MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
REPLACE INTO MetaDataReal
VALUES ('global_discount_rate', 0.05, 'Discount Rate for future costs');
REPLACE INTO MetaDataReal
VALUES ('default_loan_rate', 0.05, 'Default Loan Rate if not specified in loan_rate table');

CREATE TABLE IF NOT EXISTS capacity_factor_tech
(
    region TEXT,
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod    TEXT
        REFERENCES TimeOfDay (tod),
    tech   TEXT
        REFERENCES Technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, period, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE IF NOT EXISTS CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
CREATE TABLE IF NOT EXISTS CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO CommodityType
VALUES ('s', 'source commodity');
REPLACE INTO CommodityType
VALUES ('a', 'annual commodity');
REPLACE INTO CommodityType
VALUES ('p', 'physical commodity');
REPLACE INTO CommodityType
VALUES ('d', 'demand commodity');
REPLACE INTO CommodityType
VALUES ('e', 'emissions commodity');
CREATE TABLE IF NOT EXISTS cost_emission
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT NOT NULL
        REFERENCES Commodity (name),
    cost      REAL NOT NULL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm)
);
CREATE TABLE IF NOT EXISTS cost_fixed
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    tech    TEXT    NOT NULL
        REFERENCES Technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS cost_invest
(
    region  TEXT,
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER
        REFERENCES TimePeriod (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE IF NOT EXISTS cost_variable
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    tech    TEXT    NOT NULL
        REFERENCES Technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS Demand
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    commodity TEXT
        REFERENCES Commodity (name),
    demand    REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, commodity)
);
CREATE TABLE IF NOT EXISTS DemandSpecificDistribution
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES Commodity (name),
    dsd         REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
CREATE TABLE IF NOT EXISTS efficiency
(
    region      TEXT,
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    efficiency  REAL,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
CREATE TABLE IF NOT EXISTS emission_activity
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES Commodity (name),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    activity    REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS existing_capacity
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE IF NOT EXISTS lifetime_process
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE IF NOT EXISTS lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS limit_activity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    activity REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE IF NOT EXISTS limit_activity_share
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE IF NOT EXISTS limit_annual_capacity_factor
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    tech        TEXT
        REFERENCES Technology (tech),
    output_comm TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    factor      REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE IF NOT EXISTS limit_capacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    capacity REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE IF NOT EXISTS limit_capacity_share
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE IF NOT EXISTS limit_degrowth_capacity
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
CREATE TABLE IF NOT EXISTS limit_emission
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    value     REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm, operator)
);
CREATE TABLE IF NOT EXISTS limit_growth_capacity
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
CREATE TABLE IF NOT EXISTS limit_new_capacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    new_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE IF NOT EXISTS limit_new_capacity_share
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE IF NOT EXISTS limit_resource
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
CREATE TABLE IF NOT EXISTS limit_seasonal_capacity_factor
(
	region  TEXT
        REFERENCES Region (region),
	period	INTEGER
        REFERENCES TimePeriod (period),
	season TEXT
        REFERENCES SeasonLabel (season),
	tech    TEXT
        REFERENCES Technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
	factor	REAL,
	notes	TEXT,
	PRIMARY KEY(region, period, season, tech, operator)
);
CREATE TABLE IF NOT EXISTS LimitStorageLevelFraction
(
    region   TEXT,
    period   INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod      TEXT
        REFERENCES TimeOfDay (tod),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    fraction REAL,
    notes    TEXT,
    PRIMARY KEY(region, period, season, tod, tech, vintage, operator)
);
CREATE TABLE IF NOT EXISTS limit_tech_input_split
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
CREATE TABLE IF NOT EXISTS limit_tech_input_split_annual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
CREATE TABLE IF NOT EXISTS limit_tech_output_split
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
CREATE TABLE IF NOT EXISTS limit_tech_output_split_annual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
CREATE TABLE IF NOT EXISTS Operator
(
	operator TEXT PRIMARY KEY,
	notes TEXT
);
REPLACE INTO Operator VALUES('e','equal to');
REPLACE INTO Operator VALUES('le','less than or equal to');
REPLACE INTO Operator VALUES('ge','greater than or equal to');
CREATE TABLE IF NOT EXISTS OutputBuiltCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, tech, vintage)
);
CREATE TABLE IF NOT EXISTS OutputCost
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT REFERENCES SectorLabel (sector),
    period   INTEGER REFERENCES TimePeriod (period),
    tech     TEXT REFERENCES Technology (tech),
    vintage  INTEGER REFERENCES TimePeriod (period),
    d_invest REAL,
    d_fixed  REAL,
    d_var    REAL,
    d_emiss  REAL,
    invest   REAL,
    fixed    REAL,
    var      REAL,
    emiss    REAL,
    PRIMARY KEY (scenario, region, period, tech, vintage),
    FOREIGN KEY (vintage) REFERENCES TimePeriod (period),
    FOREIGN KEY (tech) REFERENCES Technology (tech)
);
CREATE TABLE IF NOT EXISTS OutputCurtailment
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimePeriod (period),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    curtailment REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS OutputDualVariable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
CREATE TABLE IF NOT EXISTS OutputEmission
(
    scenario  TEXT,
    region    TEXT,
    sector    TEXT
        REFERENCES SectorLabel (sector),
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT
        REFERENCES Commodity (name),
    tech      TEXT
        REFERENCES Technology (tech),
    vintage   INTEGER
        REFERENCES TimePeriod (period),
    emission  REAL,
    PRIMARY KEY (region, scenario, period, emis_comm, tech, vintage)
);
CREATE TABLE IF NOT EXISTS OutputFlowIn
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS OutputFlowOut
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS OutputNetCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    period   INTEGER
        REFERENCES TimePeriod (period),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS OutputObjective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
);
CREATE TABLE IF NOT EXISTS OutputRetiredCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    period   INTEGER
        REFERENCES TimePeriod (period),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    cap_eol REAL,
    cap_early REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS OutputStorageLevel
(
    scenario TEXT,
    region TEXT,
    sector TEXT
        REFERENCES SectorLabel (sector),
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod TEXT
        REFERENCES TimeOfDay (tod),
    tech TEXT
        REFERENCES Technology (tech),
    vintage INTEGER
        REFERENCES TimePeriod (period),
    level REAL,
    PRIMARY KEY (scenario, region, period, season, tod, tech, vintage)
);
CREATE TABLE IF NOT EXISTS Region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE IF NOT EXISTS SeasonLabel
(
    season TEXT PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE IF NOT EXISTS SectorLabel
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE IF NOT EXISTS storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS Technology
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
    FOREIGN KEY (flag) REFERENCES TechnologyType (label)
);
CREATE TABLE IF NOT EXISTS TechnologyType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO TechnologyType
VALUES ('p', 'production technology');
REPLACE INTO TechnologyType
VALUES ('pb', 'baseload production technology');
REPLACE INTO TechnologyType
VALUES ('ps', 'storage production technology');
CREATE TABLE IF NOT EXISTS TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
CREATE TABLE IF NOT EXISTS TimePeriodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO TimePeriodType
VALUES('e', 'existing vintages');
REPLACE INTO TimePeriodType
VALUES('f', 'future');
CREATE TABLE IF NOT EXISTS TimeSeason
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    season TEXT
        REFERENCES SeasonLabel (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
CREATE TABLE IF NOT EXISTS TimeSegmentFraction
(
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    segfrac REAL,
    notes   TEXT,
    PRIMARY KEY (period, season, tod),
    CHECK (segfrac >= 0 AND segfrac <= 1)
);

COMMIT;
PRAGMA FOREIGN_KEYS = 1;
