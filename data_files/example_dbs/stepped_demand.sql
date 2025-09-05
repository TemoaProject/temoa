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
INSERT INTO MetaData VALUES('myopic_base_year',2000,'');
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in LoanRate table');
INSERT INTO MetaDataReal VALUES('global_discount_rate',0.05000000000000000277,'');
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
CREATE TABLE CapacityFactorProcess
(
    region  TEXT,
    season  TEXT
        REFERENCES TimeSeason (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, season, tod, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
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
INSERT INTO CapacityFactorTech VALUES('electricville','inter','day','EF',1.0,'');
INSERT INTO CapacityFactorTech VALUES('electricville','winter','day','EF',1.0,'');
INSERT INTO CapacityFactorTech VALUES('electricville','summer','day','EF',1.0,'');
INSERT INTO CapacityFactorTech VALUES('electricville','inter','day','EH',1.0,'');
INSERT INTO CapacityFactorTech VALUES('electricville','winter','day','EH',1.0,'');
INSERT INTO CapacityFactorTech VALUES('electricville','summer','day','EH',1.0,'');
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('electricville','bulbs',1.0,'');
CREATE TABLE Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
INSERT INTO Commodity VALUES('ELC','p','# electricity');
INSERT INTO Commodity VALUES('HYD','p','# water');
INSERT INTO Commodity VALUES('co2','e','#CO2 emissions');
INSERT INTO Commodity VALUES('RL','d','# residential lighting');
INSERT INTO Commodity VALUES('earth','s','# the source of stuff');
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO CommodityType VALUES('s','source commodity');
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
CREATE TABLE CostEmission
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
INSERT INTO CostFixed VALUES('electricville',2000,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2005,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2010,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2015,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2020,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2025,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2035,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2040,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2045,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2050,'EH',1995,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2010,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2015,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2020,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2025,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2030,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2035,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2040,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2045,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2050,'EF',2010,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2000,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2005,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2010,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2015,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2020,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2025,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2030,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2035,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2040,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2045,'EH',2000,2.0,'','');
INSERT INTO CostFixed VALUES('electricville',2050,'EH',2000,2.0,'','');
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
INSERT INTO CostInvest VALUES('electricville','EF',2010,200.0,'','');
INSERT INTO CostInvest VALUES('electricville','EH',2000,100.0,'','');
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
INSERT INTO CostVariable VALUES('electricville',2010,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2015,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2020,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2025,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2030,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2035,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2040,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2045,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2050,'EF',2010,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2000,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2005,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2010,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2015,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2020,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2025,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2030,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2035,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2040,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2045,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2050,'EH',1995,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2000,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2005,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2010,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2015,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2020,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2025,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2030,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2035,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2040,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2045,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2050,'EH',2000,2.0,'','');
INSERT INTO CostVariable VALUES('electricville',2000,'well',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('electricville',2010,'well',2000,1.0,NULL,NULL);
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
INSERT INTO Demand VALUES('electricville',2000,'RL',2.0,'','');
INSERT INTO Demand VALUES('electricville',2005,'RL',2.0,'','');
INSERT INTO Demand VALUES('electricville',2010,'RL',2.0,'','');
INSERT INTO Demand VALUES('electricville',2015,'RL',2.0,'','');
INSERT INTO Demand VALUES('electricville',2020,'RL',10.0,'','');
INSERT INTO Demand VALUES('electricville',2025,'RL',10.0,'','');
INSERT INTO Demand VALUES('electricville',2030,'RL',10.0,'','');
INSERT INTO Demand VALUES('electricville',2035,'RL',50.0,'','');
INSERT INTO Demand VALUES('electricville',2040,'RL',10.0,NULL,NULL);
INSERT INTO Demand VALUES('electricville',2045,'RL',10.0,NULL,NULL);
INSERT INTO Demand VALUES('electricville',2050,'RL',2.0,NULL,NULL);
CREATE TABLE DemandSpecificDistribution
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
INSERT INTO DemandSpecificDistribution VALUES('electricville','inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville','summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville','winter','day','RL',0.3332999999999999852,'');
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
INSERT INTO Efficiency VALUES('electricville','HYD','EH',1995,'ELC',1.0,'est');
INSERT INTO Efficiency VALUES('electricville','HYD','EH',2000,'ELC',1.0,'est');
INSERT INTO Efficiency VALUES('electricville','HYD','EF',2010,'ELC',10.0,'est');
INSERT INTO Efficiency VALUES('electricville','ELC','bulbs',2000,'RL',1.0,NULL);
INSERT INTO Efficiency VALUES('electricville','earth','well',2000,'HYD',1.0,'water source');
INSERT INTO Efficiency VALUES('electricville','HYD','EH',2020,'ELC',1.0,NULL);
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
INSERT INTO EmissionActivity VALUES('electricville','co2','HYD','EH',1995,'ELC',0.05000000000000000277,'','');
INSERT INTO EmissionActivity VALUES('electricville','co2','HYD','EF',2010,'ELC',0.0100000000000000002,'','');
INSERT INTO EmissionActivity VALUES('electricville','co2','HYD','EH',2000,'ELC',0.02000000000000000041,NULL,NULL);
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
INSERT INTO ExistingCapacity VALUES('electricville','EH',1995,0.5,'','');
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
INSERT INTO TechGroup VALUES('RPS_global','');
INSERT INTO TechGroup VALUES('RPS_common','');
CREATE TABLE GrowthRateMax
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE GrowthRateSeed
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    seed   REAL,
    units  TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE LoanLifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LoanLifetimeTech VALUES('electricville','EF',50.0,'');
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
INSERT INTO LifetimeProcess VALUES('electricville','EH',1995,80.0,'#forexistingcap');
CREATE TABLE LifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LifetimeTech VALUES('electricville','EH',100.0,'');
INSERT INTO LifetimeTech VALUES('electricville','EF',100.0,'');
INSERT INTO LifetimeTech VALUES('electricville','bulbs',100.0,'super LED!');
INSERT INTO LifetimeTech VALUES('electricville','well',100.0,NULL);
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
CREATE TABLE MaxActivity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    max_act REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MaxCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    max_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
INSERT INTO MaxCapacity VALUES('electricville',2000,'EH',5.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2005,'EH',5.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2010,'EH',5.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2015,'EH',5.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2020,'EH',5.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2025,'EH',5.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2030,'EH',5.0,'','');
CREATE TABLE MaxResource
(
    region  TEXT,
    tech    TEXT
        REFERENCES Technology (tech),
    max_res REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE MinActivity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    min_act REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MaxCapacityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    max_cap    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE MinCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    min_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
INSERT INTO MinCapacity VALUES('electricville',2000,'EH',0.2000000000000000111,'','');
INSERT INTO MinCapacity VALUES('electricville',2005,'EH',0.2000000000000000111,'','');
INSERT INTO MinCapacity VALUES('electricville',2010,'EH',0.2000000000000000111,'','');
INSERT INTO MinCapacity VALUES('electricville',2015,'EH',0.2000000000000000111,'','');
CREATE TABLE MinCapacityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    min_cap    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
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
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2000,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2000,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2005,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2005,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2025,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2015,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2010,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2020,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2030,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2020,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2020,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2010,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2030,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2025,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2025,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2015,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2020,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2025,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2015,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2010,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2030,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2030,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2035,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2035,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2035,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2035,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2040,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2040,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2040,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2040,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2045,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2045,'EH',1995,0.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2045,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2045,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2050,'EH',2020,3.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2050,'EF',2010,45.0);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2050,'EH',2000,1.5);
INSERT INTO OutputNetCapacity VALUES('myo_1','electricville','electric',2050,'EH',1995,0.5);
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
INSERT INTO OutputBuiltCapacity VALUES('myo_1','electricville','electric','EH',2000,1.5);
INSERT INTO OutputBuiltCapacity VALUES('myo_1','electricville','electric','EF',2010,45.0);
INSERT INTO OutputBuiltCapacity VALUES('myo_1','electricville','electric','EH',2020,3.0);
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
    capacity REAL,
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
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2000,'summer','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2000,'inter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2000,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2000,'summer','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2000,'winter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2000,'winter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2000,'summer','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2000,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2000,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2000,'inter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2000,'inter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2000,'winter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2005,'inter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2005,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2005,'inter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2005,'winter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2005,'summer','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2005,'summer','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2005,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2005,'inter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2005,'winter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2005,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2005,'winter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2005,'summer','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2020,'winter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2030,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2020,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2025,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2020,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2020,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2015,'summer','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2010,'winter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2025,'inter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2020,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2020,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2025,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2010,'inter','day','HYD','EF',2010,'ELC',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2030,'winter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2025,'winter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2025,'summer','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2010,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2015,'winter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2020,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2025,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2010,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2020,'summer','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2020,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2015,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2025,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2020,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2015,'winter','day','HYD','EF',2010,'ELC',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2030,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2030,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2010,'summer','day','HYD','EF',2010,'ELC',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2025,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2010,'inter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2025,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2015,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2015,'inter','day','HYD','EF',2010,'ELC',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2015,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2030,'inter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2015,'inter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2025,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2015,'summer','day','HYD','EF',2010,'ELC',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2030,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2030,'summer','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2030,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2020,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2020,'inter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2030,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2010,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2030,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2010,'summer','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2030,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2010,'winter','day','HYD','EF',2010,'ELC',0.06665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2025,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2030,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2025,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EF',2010,'ELC',1.499849999999999906);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2035,'winter','day','earth','well',2000,'HYD',3.166349999999999998);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2035,'inter','day','ELC','bulbs',2000,'RL',16.66499999999999915);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2035,'summer','day','ELC','bulbs',2000,'RL',16.66499999999999915);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2035,'inter','day','earth','well',2000,'HYD',3.166349999999999998);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EF',2010,'ELC',1.499849999999999906);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2035,'winter','day','ELC','bulbs',2000,'RL',16.66499999999999915);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EF',2010,'ELC',1.499849999999999906);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2035,'summer','day','earth','well',2000,'HYD',3.166349999999999998);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2040,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2040,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2040,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2040,'inter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2040,'summer','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2040,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2040,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2040,'winter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2040,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2040,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2040,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2040,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2045,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2045,'summer','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2045,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2045,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2045,'inter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2045,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2045,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2045,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2045,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2045,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2045,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2045,'winter','day','HYD','EF',2010,'ELC',0.2333099999999999897);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2050,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2050,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2050,'summer','day','HYD','EH',2020,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','residential',2050,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2050,'winter','day','HYD','EH',2020,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2050,'inter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2050,'summer','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','supply',2050,'winter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowIn VALUES('myo_1','electricville','electric',2050,'inter','day','HYD','EH',2020,'ELC',0.6665999999999999704);
CREATE TABLE OutputFlowOut
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
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
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2000,'summer','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2000,'inter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2000,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2000,'summer','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2000,'winter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2000,'winter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2000,'summer','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2000,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2000,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2000,'inter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2000,'inter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2000,'winter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2005,'inter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2005,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2005,'inter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2005,'winter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2005,'summer','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2005,'summer','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2005,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2005,'inter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2005,'winter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2005,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2005,'winter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2005,'summer','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2020,'winter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2030,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2020,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2025,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2020,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2020,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2015,'summer','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2010,'winter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2025,'inter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2020,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2020,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2025,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2010,'inter','day','HYD','EF',2010,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2030,'winter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2025,'winter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2025,'summer','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2010,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2015,'winter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2020,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2025,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2010,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2020,'summer','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2020,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2015,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2025,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2020,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2015,'winter','day','HYD','EF',2010,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2030,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2030,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2010,'summer','day','HYD','EF',2010,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2025,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2010,'inter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2025,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2015,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2015,'inter','day','HYD','EF',2010,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2015,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2030,'inter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2015,'inter','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2025,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2015,'summer','day','HYD','EF',2010,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2030,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2030,'summer','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2030,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2020,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2020,'inter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2030,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2010,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2030,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2010,'summer','day','earth','well',2000,'HYD',0.06665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2030,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2010,'winter','day','HYD','EF',2010,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2025,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2030,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2025,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EF',2010,'ELC',14.99849999999999995);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2035,'winter','day','earth','well',2000,'HYD',3.166349999999999998);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2035,'inter','day','ELC','bulbs',2000,'RL',16.66499999999999915);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2035,'summer','day','ELC','bulbs',2000,'RL',16.66499999999999915);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2035,'inter','day','earth','well',2000,'HYD',3.166349999999999998);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EF',2010,'ELC',14.99849999999999995);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'summer','day','HYD','EH',1995,'ELC',0.1666499999999999926);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2035,'winter','day','ELC','bulbs',2000,'RL',16.66499999999999915);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'inter','day','HYD','EF',2010,'ELC',14.99849999999999995);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2035,'winter','day','HYD','EH',2000,'ELC',0.4999500000000000055);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2035,'summer','day','earth','well',2000,'HYD',3.166349999999999998);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2040,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2040,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2040,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2040,'inter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2040,'summer','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2040,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2040,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2040,'winter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2040,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2040,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2040,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2040,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2045,'summer','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2045,'summer','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2045,'inter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2045,'inter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2045,'inter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2045,'winter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2045,'summer','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2045,'winter','day','earth','well',2000,'HYD',1.233209999999999918);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2045,'summer','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2045,'winter','day','HYD','EH',2020,'ELC',0.999900000000000011);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2045,'inter','day','ELC','bulbs',2000,'RL',3.333000000000000184);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2045,'winter','day','HYD','EF',2010,'ELC',2.333099999999999952);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2050,'inter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2050,'winter','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2050,'summer','day','HYD','EH',2020,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','residential',2050,'summer','day','ELC','bulbs',2000,'RL',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2050,'winter','day','HYD','EH',2020,'ELC',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2050,'inter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2050,'summer','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','supply',2050,'winter','day','earth','well',2000,'HYD',0.6665999999999999704);
INSERT INTO OutputFlowOut VALUES('myo_1','electricville','electric',2050,'inter','day','HYD','EH',2020,'ELC',0.6665999999999999704);
CREATE TABLE PlanningReserveMargin
(
    region TEXT
        PRIMARY KEY
        REFERENCES Region (region),
    margin REAL
);
CREATE TABLE RampDown
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    PRIMARY KEY (region, tech)
);
CREATE TABLE RampUp
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    PRIMARY KEY (region, tech)
);
CREATE TABLE Region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
INSERT INTO Region VALUES('electricville',NULL);
CREATE TABLE TimeSegmentFraction
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
INSERT INTO TimeSegmentFraction VALUES('inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES('summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES('winter','day',0.3332999999999999852,'# W-D');
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE StorageInit
(
    tech  TEXT
        PRIMARY KEY,
    value REAL,
    notes TEXT
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
CREATE TABLE TechInputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech)
);
CREATE TABLE TechInputSplitAnnual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech)
);
CREATE TABLE TechOutputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm)
);
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(1,'day');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(1,1995,'e');
INSERT INTO TimePeriod VALUES(2,2000,'f');
INSERT INTO TimePeriod VALUES(3,2005,'f');
INSERT INTO TimePeriod VALUES(4,2010,'f');
INSERT INTO TimePeriod VALUES(5,2015,'f');
INSERT INTO TimePeriod VALUES(6,2020,'f');
INSERT INTO TimePeriod VALUES(7,2025,'f');
INSERT INTO TimePeriod VALUES(8,2030,'f');
INSERT INTO TimePeriod VALUES(9,2035,'f');
INSERT INTO TimePeriod VALUES(10,2040,'f');
INSERT INTO TimePeriod VALUES(11,2045,'f');
INSERT INTO TimePeriod VALUES(12,2050,'f');
INSERT INTO TimePeriod VALUES(13,2055,'f');
CREATE TABLE TimeSeason
(
    sequence INTEGER UNIQUE,
    season   TEXT
        PRIMARY KEY
);
INSERT INTO TimeSeason VALUES(1,'inter');
INSERT INTO TimeSeason VALUES(2,'summer');
INSERT INTO TimeSeason VALUES(3,'winter');
CREATE TABLE TimePeriodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TimePeriodType VALUES('e','existing vintages');
INSERT INTO TimePeriodType VALUES('f','future');
CREATE TABLE MaxActivityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MaxCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MaxAnnualCapacityFactor
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    tech        TEXT
        REFERENCES Technology (tech),
    output_comm TEXT
        REFERENCES Commodity (name),
    factor      REAL,
    source      TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE MaxNewCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    max_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MaxNewCapacityGroup
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    group_name  TEXT
        REFERENCES TechGroup (group_name),
    max_new_cap REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE MaxNewCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinActivityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinAnnualCapacityFactor
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    tech        TEXT
        REFERENCES Technology (tech),
    output_comm TEXT
        REFERENCES Commodity (name),
    factor      REAL,
    source      TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE MinCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinNewCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    min_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MinNewCapacityGroup
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    group_name  TEXT
        REFERENCES TechGroup (group_name),
    min_new_cap REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE MinNewCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
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
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2000,'co2','EH',2000,0.02999700000000000283);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2000,'co2','EH',1995,0.02499749999999999889);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2005,'co2','EH',1995,0.02499749999999999889);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2005,'co2','EH',2000,0.02999700000000000283);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2010,'co2','EF',2010,0.01999800000000000189);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2015,'co2','EF',2010,0.01999800000000000189);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2020,'co2','EF',2010,0.06999299999999999967);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2025,'co2','EF',2010,0.06999299999999999967);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2030,'co2','EF',2010,0.06999299999999999967);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2035,'co2','EF',2010,0.4499549999999999939);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2035,'co2','EH',1995,0.02499749999999999889);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2035,'co2','EH',2000,0.02999700000000000283);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2040,'co2','EF',2010,0.06999299999999999967);
INSERT INTO OutputEmission VALUES('myo_1','electricville','electric',2045,'co2','EF',2010,0.06999299999999999967);
CREATE TABLE MinActivityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    min_act    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE EmissionLimit
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT
        REFERENCES Commodity (name),
    value     REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm)
);
CREATE TABLE MaxActivityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    max_act    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
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
    variable     INTEGER NOT NULL DEFAULT 0,
    exchange     INTEGER NOT NULL DEFAULT 0,
    description  TEXT,
    FOREIGN KEY (flag) REFERENCES TechnologyType (label)
);
INSERT INTO Technology VALUES('well','r','supply','water','',1,0,0,0,0,0,0,0,'plain old water');
INSERT INTO Technology VALUES('bulbs','p','residential','electric','',1,0,0,0,0,0,0,0,' residential lighting');
INSERT INTO Technology VALUES('EH','p','electric','hydro','',0,0,0,0,0,0,0,0,'hydro power electric plant');
INSERT INTO Technology VALUES('EF','p','electric','electric','',0,0,0,0,0,0,0,0,'fusion plant');
CREATE TABLE OutputCost
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
INSERT INTO OutputCost VALUES('myo_1','electricville',2000,'EH',1995,0.0,4.545950504162363793,4.545495909111947341,0.0,0.0,5.0,4.999500000000000277,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2000,'EH',2000,61.27462483904239577,13.63785151248709226,13.63648772733584202,0.0,194.2568624481849327,15.0,14.99849999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2000,'well',2000,0.0,0.0,9.090991818223894682,0.0,0.0,0.0,9.99900000000000055,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2005,'EH',1995,0.0,3.561871171481695076,3.561514984364547054,0.0,0.0,5.0,4.999500000000000277,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2005,'EH',2000,0.0,10.68561351444508566,10.68454495309364027,0.0,0.0,15.0,14.99849999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2010,'EH',1995,0.0,2.790819264445571157,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2015,'EH',1995,0.0,2.186679919577362518,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2020,'EH',1995,0.0,1.713320934680008679,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2025,'EH',1995,0.0,1.342431783879983964,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2010,'EH',2000,0.0,8.37245779333671436,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2015,'EH',2000,0.0,6.560039758732087555,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2020,'EH',2000,0.0,5.139962804040026256,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2025,'EH',2000,0.0,4.027295351639951448,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2030,'EH',2000,0.0,3.155491288106695436,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2010,'well',2000,0.0,0.0,0.5581080365038253443,0.0,0.0,0.0,0.999900000000000011,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2010,'EF',2010,4493.317939551132441,251.1737338001014166,11.16216073007650599,0.0,14789.71858114884889,450.0,19.9980000000000011,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2015,'EF',2010,0.0,196.8011927619626248,8.745845006341619765,0.0,0.0,450.0,19.9980000000000011,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2020,'EF',2010,0.0,154.1988841212007913,23.98409443621157066,0.0,0.0,450.0,69.992999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2025,'EF',2010,0.0,120.8188605491985613,18.79216556982234465,0.0,0.0,450.0,69.992999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2030,'EF',2010,0.0,94.664738643200863,14.72415344856346131,0.0,0.0,450.0,69.992999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2035,'EH',1995,0.0,0.8241366640982862312,0.8240542504318764116,0.0,0.0,5.0,4.999500000000000277,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2035,'EH',2000,0.0,2.472409992294858583,2.472162751295629235,0.0,0.0,15.0,14.99849999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2035,'EF',2010,0.0,74.17229976884576104,74.1648825388688806,0.0,0.0,450.0,449.9549999999999841,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2040,'EH',1995,0.0,0.6457326410670342077,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2040,'EH',2000,0.0,1.937197923201102512,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2040,'EF',2010,0.0,58.1159376960330789,9.039352949240985425,0.0,0.0,450.0,69.992999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2045,'EH',1995,0.0,0.5059484208188066435,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2045,'EH',2000,0.0,1.517845262456420042,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2045,'EF',2010,0.0,45.53535787369259679,7.082569563674146807,0.0,0.0,450.0,69.992999999999995,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2050,'EH',1995,0.0,0.3964238265949301953,0.0,0.0,0.0,5.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2050,'EH',2000,0.0,1.18927147978479053,0.0,0.0,0.0,15.0,0.0,0.0);
INSERT INTO OutputCost VALUES('myo_1','electricville',2050,'EF',2010,0.0,35.67814439354371813,0.0,0.0,0.0,450.0,0.0,0.0);
CREATE TABLE MyopicEfficiency
(
    base_year   integer,
    region      text,
    input_comm  text,
    tech        text,
    vintage     integer,
    output_comm text,
    efficiency  real,
    lifetime    integer,

    FOREIGN KEY (tech) REFERENCES Technology (tech),
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm)
);
INSERT INTO MyopicEfficiency VALUES(-1,'electricville','HYD','EH',1995,'ELC',1.0,80);
INSERT INTO MyopicEfficiency VALUES(2000,'electricville','HYD','EH',2000,'ELC',1.0,100);
INSERT INTO MyopicEfficiency VALUES(2000,'electricville','ELC','bulbs',2000,'RL',1.0,100);
INSERT INTO MyopicEfficiency VALUES(2000,'electricville','earth','well',2000,'HYD',1.0,100);
INSERT INTO MyopicEfficiency VALUES(2010,'electricville','HYD','EF',2010,'ELC',10.0,100);
INSERT INTO MyopicEfficiency VALUES(2010,'electricville','HYD','EH',2020,'ELC',1.0,100);
CREATE INDEX region_tech_vintage ON MyopicEfficiency (region, tech, vintage);
COMMIT;
