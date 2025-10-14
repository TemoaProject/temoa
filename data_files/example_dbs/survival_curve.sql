PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE MetaData
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
INSERT INTO MetaData VALUES('DB_MAJOR',3,'DB major version number');
INSERT INTO MetaData VALUES('DB_MINOR',0,'DB minor version number');
INSERT INTO MetaData VALUES('days_per_period',365,'count of days in each period');
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('global_discount_rate',0.05,'Discount Rate for future costs');
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05,'Default Loan Rate if not specified in LoanRate table');
CREATE TABLE OutputDualVariable
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
INSERT INTO SeasonLabel VALUES('s',NULL);
CREATE TABLE SectorLabel
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE CapacityCredit
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER,
    credit  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage),
    CHECK (credit >= 0 AND credit <= 1)
);
CREATE TABLE CapacityFactorProcess
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES SeasonLabel (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, season, tod, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE CapacityFactorTech
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
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
INSERT INTO Commodity VALUES('source','s',NULL);
INSERT INTO Commodity VALUES('demand','d',NULL);
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('a','annual commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
INSERT INTO CommodityType VALUES('s','source commodity');
INSERT INTO CommodityType VALUES('w','waste commodity');
INSERT INTO CommodityType VALUES('wa','waste annual commodity');
INSERT INTO CommodityType VALUES('wp','waste physical commodity');
CREATE TABLE ConstructionInput
(
    region      TEXT,
    input_comm   TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage)
);
CREATE TABLE CostEmission
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
CREATE TABLE CostFixed
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
INSERT INTO CostFixed VALUES('region',2025,'tech_ancient',1994,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2025,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2030,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2035,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2040,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2025,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2030,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2035,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2040,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2045,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2050,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2030,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2035,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2040,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2045,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2050,'tech_future',2050,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2035,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2040,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2045,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2050,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2040,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2045,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2050,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2045,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2050,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('region',2050,'tech_future',2030,1.0,NULL,NULL);
CREATE TABLE CostInvest
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
INSERT INTO CostInvest VALUES('region','tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('region','tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('region','tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('region','tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('region','tech_future',2045,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('region','tech_future',2050,1.0,NULL,NULL);
CREATE TABLE CostVariable
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
INSERT INTO CostVariable VALUES('region',2025,'tech_ancient',1994,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2025,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2030,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2035,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2040,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2025,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2030,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2035,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2040,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2045,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2050,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2030,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2035,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2040,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2045,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2050,'tech_future',2050,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2035,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2040,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2045,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2050,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2040,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2045,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2050,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2045,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2050,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2050,'tech_future',2030,1.0,NULL,NULL);
CREATE TABLE Demand
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
INSERT INTO Demand VALUES('region',2025,'demand',1.0,NULL,NULL);
INSERT INTO Demand VALUES('region',2030,'demand',1.0,NULL,NULL);
INSERT INTO Demand VALUES('region',2035,'demand',1.0,NULL,NULL);
INSERT INTO Demand VALUES('region',2040,'demand',1.0,NULL,NULL);
INSERT INTO Demand VALUES('region',2045,'demand',1.0,NULL,NULL);
INSERT INTO Demand VALUES('region',2050,'demand',1.0,NULL,NULL);
CREATE TABLE DemandSpecificDistribution
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
CREATE TABLE EndOfLifeOutput
(
    region      TEXT,
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm   TEXT
        REFERENCES Commodity (name),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, tech, vintage, output_comm)
);
CREATE TABLE Efficiency
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
INSERT INTO Efficiency VALUES('region','source','tech_ancient',1994,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_old',2010,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_current',2025,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_future',2030,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_future',2035,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_future',2040,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_future',2045,'demand',1.0,NULL);
INSERT INTO Efficiency VALUES('region','source','tech_future',2050,'demand',1.0,NULL);
CREATE TABLE EfficiencyVariable
(
    region      TEXT,
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
    efficiency  REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
CREATE TABLE EmissionActivity
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
CREATE TABLE EmissionEmbodied
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm,  tech, vintage)
);
CREATE TABLE EmissionEndOfLife
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm,  tech, vintage)
);
CREATE TABLE ExistingCapacity
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
INSERT INTO ExistingCapacity VALUES('region','tech_ancient',1994,3.0,NULL,NULL);
INSERT INTO ExistingCapacity VALUES('region','tech_old',2010,0.7,NULL,NULL);
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
CREATE TABLE LoanLifetimeProcess
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
CREATE TABLE LoanRate
(
    region  TEXT,
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER
        REFERENCES TimePeriod (period),
    rate    REAL,
    notes   TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE LifetimeProcess
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
CREATE TABLE LifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LifetimeTech VALUES('region','tech_ancient',35.0,NULL);
INSERT INTO LifetimeTech VALUES('region','tech_old',35.0,NULL);
INSERT INTO LifetimeTech VALUES('region','tech_current',35.0,NULL);
INSERT INTO LifetimeTech VALUES('region','tech_future',35.0,NULL);
CREATE TABLE Operator
(
	operator TEXT PRIMARY KEY,
	notes TEXT
);
INSERT INTO Operator VALUES('e','equal to');
INSERT INTO Operator VALUES('le','less than or equal to');
INSERT INTO Operator VALUES('ge','greater than or equal to');
CREATE TABLE LimitGrowthCapacity
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
CREATE TABLE LimitDegrowthCapacity
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
CREATE TABLE LimitGrowthNewCapacity
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
CREATE TABLE LimitDegrowthNewCapacity
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
CREATE TABLE LimitGrowthNewCapacityDelta
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
CREATE TABLE LimitDegrowthNewCapacityDelta
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
CREATE TABLE LimitActivity
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
CREATE TABLE LimitActivityShare
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
CREATE TABLE LimitAnnualCapacityFactor
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
CREATE TABLE LimitCapacity
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
CREATE TABLE LimitCapacityShare
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
CREATE TABLE LimitNewCapacity
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
CREATE TABLE LimitNewCapacityShare
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
CREATE TABLE LimitResource
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
CREATE TABLE LimitSeasonalCapacityFactor
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
CREATE TABLE LimitTechInputSplit
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
CREATE TABLE LimitTechInputSplitAnnual
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
CREATE TABLE LimitTechOutputSplit
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
CREATE TABLE LimitTechOutputSplitAnnual
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
CREATE TABLE LimitEmission
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
CREATE TABLE LinkedTech
(
    primary_region TEXT,
    primary_tech   TEXT
        REFERENCES Technology (tech),
    emis_comm      TEXT
        REFERENCES Commodity (name),
    driven_tech    TEXT
        REFERENCES Technology (tech),
    notes          TEXT,
    PRIMARY KEY (primary_region, primary_tech, emis_comm)
);
CREATE TABLE OutputCurtailment
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
CREATE TABLE OutputNetCapacity
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
CREATE TABLE OutputBuiltCapacity
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
CREATE TABLE OutputRetiredCapacity
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
CREATE TABLE OutputFlowIn
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
CREATE TABLE OutputFlowOut
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
CREATE TABLE OutputStorageLevel
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
CREATE TABLE PlanningReserveMargin
(
    region TEXT
        PRIMARY KEY
        REFERENCES Region (region),
    margin REAL,
    notes TEXT
);
CREATE TABLE RampDownHourly
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE RampUpHourly
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE Region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
INSERT INTO Region VALUES('region',NULL);
CREATE TABLE ReserveCapacityDerate
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    season  TEXT
    	REFERENCES SeasonLabel (season),
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, season, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE TimeSegmentFraction
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
INSERT INTO TimeSegmentFraction VALUES(2025,'s','d',1.0,NULL);
INSERT INTO TimeSegmentFraction VALUES(2030,'s','d',1.0,NULL);
INSERT INTO TimeSegmentFraction VALUES(2035,'s','d',1.0,NULL);
INSERT INTO TimeSegmentFraction VALUES(2040,'s','d',1.0,NULL);
INSERT INTO TimeSegmentFraction VALUES(2045,'s','d',1.0,NULL);
INSERT INTO TimeSegmentFraction VALUES(2050,'s','d',1.0,NULL);
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE LifetimeSurvivalCurve
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL,
    tech    TEXT    NOT NULL
        REFERENCES Technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    fraction  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
INSERT INTO LifetimeSurvivalCurve VALUES('region',1994,'tech_ancient',1994,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',1999,'tech_ancient',1994,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2004,'tech_ancient',1994,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2009,'tech_ancient',1994,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2014,'tech_ancient',1994,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2019,'tech_ancient',1994,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2029,'tech_ancient',1994,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2010,'tech_old',2010,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2015,'tech_old',2010,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2020,'tech_old',2010,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2025,'tech_old',2010,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2030,'tech_old',2010,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2035,'tech_old',2010,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2045,'tech_old',2010,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2025,'tech_current',2025,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2030,'tech_current',2025,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2035,'tech_current',2025,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2040,'tech_current',2025,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2045,'tech_current',2025,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2050,'tech_current',2025,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2060,'tech_current',2025,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2030,'tech_future',2030,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2035,'tech_future',2030,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2040,'tech_future',2030,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2045,'tech_future',2030,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2050,'tech_future',2030,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2055,'tech_future',2030,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2065,'tech_future',2030,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2035,'tech_future',2035,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2040,'tech_future',2035,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2045,'tech_future',2035,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2050,'tech_future',2035,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2055,'tech_future',2035,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2060,'tech_future',2035,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2070,'tech_future',2035,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2040,'tech_future',2040,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2045,'tech_future',2040,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2050,'tech_future',2040,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2055,'tech_future',2040,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2060,'tech_future',2040,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2065,'tech_future',2040,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2075,'tech_future',2040,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2045,'tech_future',2045,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2050,'tech_future',2045,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2055,'tech_future',2045,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2060,'tech_future',2045,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2065,'tech_future',2045,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2070,'tech_future',2045,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2080,'tech_future',2045,0.0,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2050,'tech_future',2050,1,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2055,'tech_future',2050,0.96999999999999992894,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2060,'tech_future',2050,0.88000000000000007105,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2065,'tech_future',2050,0.62000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2070,'tech_future',2050,0.27000000000000001776,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2075,'tech_future',2050,0.08,NULL);
INSERT INTO LifetimeSurvivalCurve VALUES('region',2085,'tech_future',2050,0.0,NULL);
CREATE TABLE TechnologyType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TechnologyType VALUES('p','production technology');
INSERT INTO TechnologyType VALUES('pb','baseload production technology');
INSERT INTO TechnologyType VALUES('ps','storage production technology');
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(0,'d');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(-2,1994,'e');
INSERT INTO TimePeriod VALUES(-1,2010,'e');
INSERT INTO TimePeriod VALUES(0,2025,'f');
INSERT INTO TimePeriod VALUES(1,2030,'f');
INSERT INTO TimePeriod VALUES(2,2035,'f');
INSERT INTO TimePeriod VALUES(3,2040,'f');
INSERT INTO TimePeriod VALUES(4,2045,'f');
INSERT INTO TimePeriod VALUES(5,2050,'f');
INSERT INTO TimePeriod VALUES(6,2055,'f');
CREATE TABLE TimeSeason
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    season TEXT
        REFERENCES SeasonLabel (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
INSERT INTO TimeSeason VALUES(2025,0,'s',NULL);
INSERT INTO TimeSeason VALUES(2030,1,'s',NULL);
INSERT INTO TimeSeason VALUES(2035,2,'s',NULL);
INSERT INTO TimeSeason VALUES(2040,3,'s',NULL);
INSERT INTO TimeSeason VALUES(2045,4,'s',NULL);
INSERT INTO TimeSeason VALUES(2050,5,'s',NULL);
CREATE TABLE TimeSeasonSequential
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    seas_seq TEXT,
    season TEXT
        REFERENCES SeasonLabel (season),
    num_days REAL NOT NULL,
    notes TEXT,
    PRIMARY KEY (period, sequence, seas_seq, season),
    CHECK (num_days > 0)
);
CREATE TABLE TimePeriodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TimePeriodType VALUES('e','existing vintages');
INSERT INTO TimePeriodType VALUES('f','future');
CREATE TABLE OutputEmission
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
CREATE TABLE RPSRequirement
(
    region      TEXT    NOT NULL
        REFERENCES Region (region),
    period      INTEGER NOT NULL
        REFERENCES TimePeriod (period),
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
        REFERENCES Technology (tech),
    PRIMARY KEY (group_name, tech)
);
CREATE TABLE Technology
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
INSERT INTO Technology VALUES('tech_ancient','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('tech_old','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('tech_current','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('tech_future','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
CREATE TABLE OutputCost
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
COMMIT;
