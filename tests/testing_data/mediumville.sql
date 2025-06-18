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
INSERT INTO MetaData VALUES('DB_MINOR',1,'DB minor version number');
INSERT INTO MetaData VALUES('myopic_base_year',2000,'');
INSERT INTO MetaData VALUES ('days_per_period', 365, 'count of days in each period');
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in LoanRate table');
INSERT INTO MetaDataReal VALUES('global_discount_rate',0.42000000000000004,'');
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
CREATE TABLE SectorLabel
(
    sector TEXT,
    PRIMARY KEY (sector)
);
INSERT INTO SectorLabel VALUES('supply');
INSERT INTO SectorLabel VALUES('electric');
INSERT INTO SectorLabel VALUES('transport');
INSERT INTO SectorLabel VALUES('commercial');
INSERT INTO SectorLabel VALUES('residential');
INSERT INTO SectorLabel VALUES('industrial');
CREATE TABLE CapacityCredit
(
    region  TEXT,
    period  INTEGER,
    tech    TEXT,
    vintage INTEGER,
    credit  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage),
    CHECK (credit >= 0 AND credit <= 1)
);
INSERT INTO CapacityCredit VALUES('A',2025,'EF',2025,0.5999999999999999778,NULL);
CREATE TABLE CapacityFactorProcess
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    season  TEXT
        REFERENCES TimeSeason (season),
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
INSERT INTO CapacityFactorProcess VALUES('A',2025,'s2','d1','EFL',2025,0.8000000000000000444,NULL);
INSERT INTO CapacityFactorProcess VALUES('A',2025,'s1','d2','EFL',2025,0.9000000000000000222,NULL);
CREATE TABLE CapacityFactorTech
(
    region TEXT,
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES TimeSeason (season),
    tod    TEXT
        REFERENCES TimeOfDay (tod),
    tech   TEXT
        REFERENCES Technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, period, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO CapacityFactorTech VALUES('A',2025,'s1','d1','EF',0.8000000000000000444,NULL);
INSERT INTO CapacityFactorTech VALUES('B',2025,'s2','d2','bulbs',0.75,NULL);
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('A','bulbs',1.0,'');
INSERT INTO CapacityToActivity VALUES('B','bulbs',1.0,NULL);
CREATE TABLE Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
INSERT INTO Commodity VALUES('ELC','p','electricity');
INSERT INTO Commodity VALUES('HYD','p','water');
INSERT INTO Commodity VALUES('co2','e','CO2 emissions');
INSERT INTO Commodity VALUES('RL','d','residential lighting');
INSERT INTO Commodity VALUES('earth','s','the source of stuff');
INSERT INTO Commodity VALUES('RH','d','residential heat');
INSERT INTO Commodity VALUES('FusionGas','e','mystery emission');
INSERT INTO Commodity VALUES('FusionGasFuel','p','converted mystery gas to fuel');
INSERT INTO Commodity VALUES('GeoHyd','p','Hot water from geo');
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO CommodityType VALUES('w','waste commodity');
INSERT INTO CommodityType VALUES('wa','waste annual commodity');
INSERT INTO CommodityType VALUES('wp','waste physical commodity');
INSERT INTO CommodityType VALUES('a','annual commodity');
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
INSERT INTO CommodityType VALUES('s','source commodity');
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
INSERT INTO CostEmission VALUES('A',2025,'co2',1.989999999999999992,'dollars','none');
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
INSERT INTO CostFixed VALUES('A',2025,'EH',2025,3.299999999999999823,'','');
INSERT INTO CostFixed VALUES('A',2025,'EF',2025,2.0,NULL,NULL);
INSERT INTO CostFixed VALUES('A',2025,'EFL',2025,3.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'batt',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'EF',2025,2.0,NULL,NULL);
INSERT INTO CostFixed VALUES('A',2025,'bulbs',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'bulbs',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('A',2025,'heater',2025,2.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'heater',2025,2.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'GeoThermal',2025,6.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'GeoHeater',2025,1.0,NULL,NULL);
INSERT INTO CostFixed VALUES('B',2025,'EH',2025,3.299999999999999823,NULL,NULL);
INSERT INTO CostFixed VALUES('A',2025,'GeoThermal',2025,4.0,NULL,NULL);
INSERT INTO CostFixed VALUES('A',2025,'GeoHeater',2025,4.5,NULL,NULL);
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
INSERT INTO CostInvest VALUES('A','EF',2025,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('A','EH',2025,3.0,NULL,NULL);
INSERT INTO CostInvest VALUES('A','bulbs',2025,4.0,NULL,NULL);
INSERT INTO CostInvest VALUES('A','heater',2025,5.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','EF',2025,6.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','batt',2025,7.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','bulbs',2025,8.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','heater',2025,9.0,NULL,NULL);
INSERT INTO CostInvest VALUES('A','EFL',2025,2.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','GeoThermal',2025,3.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','GeoHeater',2025,4.0,NULL,NULL);
INSERT INTO CostInvest VALUES('B','EH',2025,3.299999999999999823,NULL,NULL);
INSERT INTO CostInvest VALUES('A','GeoThermal',2025,5.599999999999999645,NULL,NULL);
INSERT INTO CostInvest VALUES('A','GeoHeater',2025,4.200000000000000177,NULL,NULL);
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
INSERT INTO CostVariable VALUES('A',2025,'EF',2025,9.0,NULL,NULL);
INSERT INTO CostVariable VALUES('A',2025,'EFL',2025,8.0,NULL,NULL);
INSERT INTO CostVariable VALUES('A',2025,'EH',2025,7.0,NULL,NULL);
INSERT INTO CostVariable VALUES('A',2025,'bulbs',2025,6.0,NULL,NULL);
INSERT INTO CostVariable VALUES('A',2025,'heater',2025,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('B',2025,'EF',2025,4.0,NULL,NULL);
INSERT INTO CostVariable VALUES('B',2025,'batt',2025,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('B',2025,'bulbs',2025,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('B',2025,'heater',2025,1.0,NULL,NULL);
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
INSERT INTO Demand VALUES('A',2025,'RL',100.0,'','');
INSERT INTO Demand VALUES('B',2025,'RL',100.0,NULL,NULL);
INSERT INTO Demand VALUES('A',2025,'RH',50.0,NULL,NULL);
INSERT INTO Demand VALUES('B',2025,'RH',50.0,NULL,NULL);
CREATE TABLE DemandSpecificDistribution
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimeSeason (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES Commodity (name),
    dsd         REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s1','d1','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s1','d2','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s2','d1','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s2','d2','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s1','d1','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s1','d2','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s2','d1','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s2','d2','RL',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s1','d1','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s2','d1','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s1','d1','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s2','d1','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s1','d2','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('A',2025,'s2','d2','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s1','d2','RH',0.25,NULL);
INSERT INTO DemandSpecificDistribution VALUES('B',2025,'s2','d2','RH',0.25,NULL);
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
INSERT INTO Efficiency VALUES('A','ELC','bulbs',2025,'RL',1.0,NULL);
INSERT INTO Efficiency VALUES('A','HYD','EH',2025,'ELC',1.0,NULL);
INSERT INTO Efficiency VALUES('A','HYD','EF',2025,'ELC',1.0,NULL);
INSERT INTO Efficiency VALUES('B','ELC','bulbs',2025,'RL',1.0,NULL);
INSERT INTO Efficiency VALUES('B','HYD','EH',2025,'ELC',1.0,NULL);
INSERT INTO Efficiency VALUES('B','ELC','batt',2025,'ELC',1.0,NULL);
INSERT INTO Efficiency VALUES('B','HYD','EF',2025,'ELC',1.0,NULL);
INSERT INTO Efficiency VALUES('A','earth','well',2025,'HYD',1.0,NULL);
INSERT INTO Efficiency VALUES('B','earth','well',2025,'HYD',1.0,NULL);
INSERT INTO Efficiency VALUES('A','earth','EFL',2025,'FusionGasFuel',1.0,NULL);
INSERT INTO Efficiency VALUES('A','FusionGasFuel','heater',2025,'RH',0.9000000000000000222,NULL);
INSERT INTO Efficiency VALUES('A-B','FusionGasFuel','FGF_pipe',2025,'FusionGasFuel',0.949999999999999956,NULL);
INSERT INTO Efficiency VALUES('B','FusionGasFuel','heater',2025,'RH',0.9000000000000000222,NULL);
INSERT INTO Efficiency VALUES('B','GeoHyd','GeoHeater',2025,'RH',0.980000000000000094,NULL);
INSERT INTO Efficiency VALUES('B','earth','GeoThermal',2025,'GeoHyd',1.0,NULL);
INSERT INTO Efficiency VALUES('B-A','FusionGasFuel','FGF_pipe',2025,'FusionGasFuel',0.949999999999999956,NULL);
INSERT INTO Efficiency VALUES('A','GeoHyd','GeoHeater',2025,'RH',0.9000000000000000222,NULL);
INSERT INTO Efficiency VALUES('A','earth','GeoThermal',2025,'GeoHyd',1.0,NULL);
CREATE TABLE EfficiencyVariable
(
    region      TEXT,
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
INSERT INTO EmissionActivity VALUES('A','co2','HYD','EH',2025,'ELC',0.02000000000000000041,NULL,NULL);
INSERT INTO EmissionActivity VALUES('A','FusionGas','HYD','EF',2025,'ELC',-0.2000000000000000111,NULL,'needs to be negative as a driver of linked tech...don''t ask');
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
INSERT INTO ExistingCapacity VALUES('A','EH',2020,200.0,'things',NULL);
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
INSERT INTO TechGroup VALUES('RPS_common','');
INSERT INTO TechGroup VALUES('A_tech_grp_1','converted from old db');
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
INSERT INTO LoanLifetimeProcess VALUES('A','EF',2025,57,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','EFL',2025,68,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','bulbs',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','EH',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','well',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','heater',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','GeoHeater',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A','GeoThermal',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','EF',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','bulbs',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','EH',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','batt',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','well',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','heater',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','GeoHeater',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B','GeoThermal',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('A-B','FGF_pipe',2025,10,NULL);
INSERT INTO LoanLifetimeProcess VALUES('B-A','FGF_pipe',2025,10,NULL);
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
INSERT INTO LifetimeProcess VALUES('B','EF',2025,200.0,NULL);
CREATE TABLE LifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LifetimeTech VALUES('A','EH',60.0,'');
INSERT INTO LifetimeTech VALUES('B','bulbs',100.0,'super LED!');
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
    season   TEXT
        REFERENCES TimeSeason (season),
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
INSERT INTO LimitActivity VALUES('A',2025,'EF','ge',0.00100000000000000002,'PJ/CY','goofy units');
INSERT INTO LimitActivity VALUES('B',2025,'EH','le',10000.0,'stuff',NULL);
INSERT INTO LimitActivity VALUES('A',2025,'EF','le',10000.0,'stuff',NULL);
INSERT INTO LimitActivity VALUES('A',2025,'A_tech_grp_1','ge',0.05000000000000000277,'',NULL);
INSERT INTO LimitActivity VALUES('A',2025,'A_tech_grp_1','le',10000.0,'',NULL);
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
    PRIMARY KEY (region, period, tech, operator),
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
INSERT INTO LimitCapacity VALUES('A',2025,'EH','ge',0.1000000000000000055,'','');
INSERT INTO LimitCapacity VALUES('B',2025,'batt','ge',0.1000000000000000055,'','');
INSERT INTO LimitCapacity VALUES('A',2025,'EH','le',20000.0,'','');
INSERT INTO LimitCapacity VALUES('B',2025,'EH','le',20000.0,'','');
INSERT INTO LimitCapacity VALUES('A',2025,'A_tech_grp_1','ge',0.2000000000000000111,'',NULL);
INSERT INTO LimitCapacity VALUES('A',2025,'A_tech_grp_1','le',6000.0,'',NULL);
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
INSERT INTO LimitNewCapacityShare VALUES('A',2025,'RPS_common','A_tech_grp_1','ge',0.0,'');
INSERT INTO LimitNewCapacityShare VALUES('global',2025,'RPS_common','A_tech_grp_1','le',1.0,'');
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
INSERT INTO LimitResource VALUES('B','EF','le',9000.0,'clumps',NULL);
CREATE TABLE LimitSeasonalCapacityFactor
(
	region  TEXT
        REFERENCES Region (region),
	period	INTEGER
        REFERENCES TimePeriod (period),
	season	TEXT
        REFERENCES TimeSeason (season),
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
INSERT INTO LimitTechInputSplit VALUES('A',2025,'HYD','EH','ge',0.949999999999999956,'95% HYD reqt.  (other not specified...)');
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
INSERT INTO LimitTechOutputSplit VALUES('B',2025,'EH','ELC','ge',0.949999999999999956,'95% ELC output (there are not others, this is a min)');
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
INSERT INTO LimitEmission VALUES('A',2025,'co2','le',10000.0,'gulps',NULL);
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
INSERT INTO LinkedTech VALUES('A','EF','FusionGas','EFL',NULL);
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
CREATE TABLE OutputFlowOut
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
CREATE TABLE OutputStorageLevel
(
    scenario TEXT,
    region TEXT,
    sector TEXT
        REFERENCES SectorLabel (sector),
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES TimeSeason (season),
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
    margin REAL
);
INSERT INTO PlanningReserveMargin VALUES('A',0.05000000000000000277);
CREATE TABLE RampDownHourly
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    PRIMARY KEY (region, tech)
);
INSERT INTO RampDownHourly VALUES('A','EH',0.05000000000000000277);
INSERT INTO RampDownHourly VALUES('B','EH',0.05000000000000000277);
CREATE TABLE RampUpHourly
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    PRIMARY KEY (region, tech)
);
INSERT INTO RampUpHourly VALUES('B','EH',0.05000000000000000277);
INSERT INTO RampUpHourly VALUES('A','EH',0.05000000000000000277);
CREATE TABLE Region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
INSERT INTO Region VALUES('A','main region');
INSERT INTO Region VALUES('B','just a 2nd region');
CREATE TABLE TimeSegmentFraction
(   
    period INTEGER
        REFERENCES TimePeriod (period),
    season  TEXT
        REFERENCES TimeSeason (season),
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
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO StorageDuration VALUES('B','batt',15.0,NULL);
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
CREATE TABLE TechnologyType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TechnologyType VALUES('r','resource technology');
INSERT INTO TechnologyType VALUES('p','production technology');
INSERT INTO TechnologyType VALUES('pb','baseload production technology');
INSERT INTO TechnologyType VALUES('ps','storage production technology');
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(1,'d1');
INSERT INTO TimeOfDay VALUES(2,'d2');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(1,2020,'e');
INSERT INTO TimePeriod VALUES(2,2025,'f');
INSERT INTO TimePeriod VALUES(3,2030,'f');
CREATE TABLE TimeSeason
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    season TEXT
        REFERENCES TimeSeason (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
INSERT INTO TimeSeason VALUES(2025,1,'s1',NULL);
INSERT INTO TimeSeason VALUES(2025,2,'s2',NULL);
CREATE TABLE TimeSeasonSequential
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    seas_seq TEXT,
    season TEXT
        REFERENCES TimeSeason (season),
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
INSERT INTO RPSRequirement VALUES('B',2025,'RPS_common',0.2999999999999999889,NULL);
CREATE TABLE TechGroupMember
(
    group_name TEXT
        REFERENCES TechGroup (group_name),
    tech       TEXT
        REFERENCES Technology (tech),
    PRIMARY KEY (group_name, tech)
);
INSERT INTO TechGroupMember VALUES('RPS_common','EF');
INSERT INTO TechGroupMember VALUES('A_tech_grp_1','EH');
INSERT INTO TechGroupMember VALUES('A_tech_grp_1','EF');
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
INSERT INTO Technology VALUES('well','r','supply','water','',0,0,0,0,0,0,0,0,'plain old water');
INSERT INTO Technology VALUES('bulbs','p','residential','electric','',0,0,0,0,0,0,0,0,'residential lighting');
INSERT INTO Technology VALUES('EH','pb','electric','hydro','',0,0,0,1,1,0,0,0,'hydro power electric plant');
INSERT INTO Technology VALUES('batt','ps','electric','electric','',0,0,0,0,0,0,0,0,'big battery');
INSERT INTO Technology VALUES('EF','p','electric','electric','',0,0,1,0,0,0,0,0,'fusion plant');
INSERT INTO Technology VALUES('EFL','p','electric','electric','',0,0,0,0,0,1,0,0,'linked (to Fusion) producer');
INSERT INTO Technology VALUES('heater','p','residential','electric','',0,0,0,0,0,0,0,0,'heater');
INSERT INTO Technology VALUES('FGF_pipe','p','transport',NULL,'',0,0,0,0,0,0,1,0,'transportation line A->B');
INSERT INTO Technology VALUES('GeoThermal','p','residential','hydro','',0,1,0,0,0,0,0,0,'geothermal hot water source');
INSERT INTO Technology VALUES('GeoHeater','p','residential','hydro','',0,0,0,0,0,0,0,0,'geothermal heater from geo hyd');
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
