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
VALUES ('DB_MINOR', 0, 'DB minor version number');
CREATE TABLE IF NOT EXISTS OutputObjective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
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
CREATE TABLE CapacityFactorTech
(
    region TEXT,
    season TEXT
        REFERENCES TimeSeason (season),
    tod    TEXT
        REFERENCES TimeOfDay (tod),
    tech   TEXT
        REFERENCES Technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE IF NOT EXISTS Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
REPLACE INTO Commodity
VALUES ('ethos', 's', NULL);
REPLACE INTO Commodity
VALUES ('fuel', 'p', NULL);
REPLACE INTO Commodity
VALUES ('carrier', 'p', NULL);
REPLACE INTO Commodity
VALUES ('demand', 'd', NULL);
CREATE TABLE IF NOT EXISTS CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO CommodityType
VALUES ('p', 'physical commodity');
REPLACE INTO CommodityType
VALUES ('d', 'demand commodity');
REPLACE INTO CommodityType
VALUES ('s', 'source commodity');
CREATE TABLE IF NOT EXISTS CostEmission
(
    region    TEXT
        REFERENCES Region (region),
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT NOT NULL
        REFERENCES Commodity (name),
    cost      REAL NOT NULL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm)
);
CREATE TABLE IF NOT EXISTS CostFixed
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
CREATE TABLE IF NOT EXISTS CostInvest
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
CREATE TABLE IF NOT EXISTS CostVariable
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
REPLACE INTO Demand
VALUES ('region', 2000, 'demand', 1, NULL, NULL);
CREATE TABLE IF NOT EXISTS DemandSpecificDistribution
(
    region      TEXT,
    season      TEXT
        REFERENCES TimeSeason (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES Commodity (name),
    dsd         REAL,
    dsd_notes   TEXT,
    PRIMARY KEY (region, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
REPLACE INTO DemandSpecificDistribution
VALUES ('region','S1', 'D1', 'demand', 0.25, NULL);
REPLACE INTO DemandSpecificDistribution
VALUES ('region','S1', 'D2', 'demand',  0.25, NULL);
REPLACE INTO DemandSpecificDistribution
VALUES ('region','S2', 'D1', 'demand',  0.25, NULL);
REPLACE INTO DemandSpecificDistribution
VALUES ('region','S2', 'D2', 'demand',  0.25, NULL);
CREATE TABLE IF NOT EXISTS Efficiency
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
REPLACE INTO Efficiency
VALUES ('region', 'ethos', 'importer', 2000, 'fuel', 1, NULL);
REPLACE INTO Efficiency
VALUES ('region', 'fuel', 'producer', 2000, 'carrier', 1, NULL);
REPLACE INTO Efficiency
VALUES ('region', 'carrier', 'consumer', 2000, 'demand', 1, NULL);
CREATE TABLE IF NOT EXISTS EmissionActivity
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
CREATE TABLE IF NOT EXISTS ExistingCapacity
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
CREATE TABLE IF NOT EXISTS LifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
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
    capacity REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS OutputFlowIn
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimeSeason (season),
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
    season      TEXT
        REFERENCES TimeSeason (season),
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
CREATE TABLE IF NOT EXISTS OutputDualVariable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
CREATE TABLE IF NOT EXISTS Region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
REPLACE INTO Region
VALUES ('region', NULL);
CREATE TABLE SectorLabel
(
    sector TEXT,
    PRIMARY KEY (sector)
);
CREATE TABLE IF NOT EXISTS StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS TimeSegmentFraction
(
    season  TEXT
        REFERENCES TimeSeason (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    segfrac REAL,
    notes   TEXT,
    PRIMARY KEY (season, tod),
    CHECK (segfrac >= 0 AND segfrac <= 1)
);
REPLACE INTO TimeSegmentFraction
VALUES ('S1', 'D1', 0.25, NULL);
REPLACE INTO TimeSegmentFraction
VALUES ('S1', 'D2', 0.25, NULL);
REPLACE INTO TimeSegmentFraction
VALUES ('S2', 'D1', 0.25, NULL);
REPLACE INTO TimeSegmentFraction
VALUES ('S2', 'D2', 0.25, NULL);
CREATE TABLE IF NOT EXISTS TechnologyType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO TechnologyType
VALUES ('r', 'resource technology');
REPLACE INTO TechnologyType
VALUES ('p', 'production technology');
REPLACE INTO TechnologyType
VALUES ('pb', 'baseload production technology');
REPLACE INTO TechnologyType
VALUES ('ps', 'storage production technology');
CREATE TABLE IF NOT EXISTS TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
REPLACE INTO TimePeriod
VALUES (0, 2000, 'f');
REPLACE INTO TimePeriod
VALUES (1, 2001, 'f');
CREATE TABLE IF NOT EXISTS TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
REPLACE INTO TimeOfDay
VALUES (0, 'D1');
REPLACE INTO TimeOfDay
VALUES (1, 'D2');
CREATE TABLE IF NOT EXISTS TimeSeason
(
    sequence INTEGER UNIQUE,
    season   TEXT
        PRIMARY KEY
);
REPLACE INTO TimeSeason
VALUES (0, 'S1');
REPLACE INTO TimeSeason
VALUES (1, 'S2');
CREATE TABLE IF NOT EXISTS TimePeriodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO TimePeriodType VALUES ('e', 'existing');
REPLACE INTO TimePeriodType VALUES ('f', 'future');
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
CREATE TABLE IF NOT EXISTS Technology
(
    tech         TEXT NOT NULL PRIMARY KEY,
    flag         TEXT NOT NULL,
    sector       TEXT,
    category     TEXT,
    sub_category TEXT,
    unlim_cap    INTEGER NOT NULL DEFAULT 0,
    annual       INTEGER NOT NULL DEFAULT 0,
    reserve      INTEGER NOT NULL DEFAULT 0,
    curtail      INTEGER NOT NULL DEFAULT 0,
    retire       INTEGER NOT NULL DEFAULT 0,
    flex         INTEGER NOT NULL DEFAULT 0,
    variable     INTEGER NOT NULL DEFAULT 0,
    exchange     INTEGER NOT NULL DEFAULT 0,
    description  TEXT,
    FOREIGN KEY (flag) REFERENCES TechnologyType (label)
);
REPLACE INTO Technology
VALUES ('importer', 'r', 'sector', NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, NULL);
REPLACE INTO Technology
VALUES ('producer', 'p', 'sector', NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, NULL);
REPLACE INTO Technology
VALUES ('consumer', 'p', 'sector', NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, NULL);
CREATE TABLE IF NOT EXISTS OutputCost
(
    scenario TEXT,
    region   TEXT,
    period   INTEGER,
    tech     TEXT,
    vintage  INTEGER,
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
COMMIT;
PRAGMA FOREIGN_KEYS = 1;
