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
INSERT INTO MetaData VALUES('link_seasons',1,'Carry storage states between seasons');
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
INSERT INTO Commodity VALUES('earth','p','# the source of stuff');
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
INSERT INTO CommodityType VALUES('s','source commodity');
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
INSERT INTO CostFixed VALUES('electricville',2025,'EH',2025,100.0,'','');
INSERT INTO CostFixed VALUES('electricville',2025,'batt',2025,1.0,'','');
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
INSERT INTO CostInvest VALUES('electricville','EH',2025,100.0,'','');
INSERT INTO CostInvest VALUES('electricville','batt',2025,1.0,NULL,NULL);
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
INSERT INTO CostVariable VALUES('electricville',2025,'EH',2025,1000.0,'','');
INSERT INTO CostVariable VALUES('electricville',2025,'batt',2025,1.0,'','');
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
INSERT INTO Demand VALUES('electricville',2025,'RL',100.0,'','');
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
INSERT INTO DemandSpecificDistribution VALUES('electricville','s1','d1','RL',0.07499999999999999723,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville','s1','d2','RL',0.07499999999999999723,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville','s1','d3','RL',0.07499999999999999723,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s2','d1','RL',0.07499999999999999723,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s2','d2','RL',0.07499999999999999723,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s2','d3','RL',0.07499999999999999723,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s1','d4','RL',0.07499999999999999723,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s1','d5','RL',0.2000000000000000111,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s2','d4','RL',0.2000000000000000111,NULL);
INSERT INTO DemandSpecificDistribution VALUES('electricville','s2','d5','RL',0.07499999999999999723,NULL);
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
INSERT INTO Efficiency VALUES('electricville','HYD','EH',2025,'ELC',1.0,NULL);
INSERT INTO Efficiency VALUES('electricville','ELC','bulbs',2025,'RL',1.0,NULL);
INSERT INTO Efficiency VALUES('electricville','earth','well',2025,'HYD',1.0,'water source');
INSERT INTO Efficiency VALUES('electricville','ELC','batt',2025,'ELC',0.75,NULL);
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
INSERT INTO EmissionActivity VALUES('electricville','co2','HYD','EH',2025,'ELC',0.02000000000000000041,NULL,NULL);
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
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
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
INSERT INTO LifetimeTech VALUES('electricville','EH',60.0,'');
INSERT INTO LifetimeTech VALUES('electricville','bulbs',100.0,'super LED!');
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
INSERT INTO MaxCapacity VALUES('electricville',2025,'EH',200.0,'','');
INSERT INTO MaxCapacity VALUES('electricville',2025,'batt',100.0,'','');
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
INSERT INTO MinCapacity VALUES('electricville',2025,'EH',0.1000000000000000055,'','');
INSERT INTO MinCapacity VALUES('electricville',2025,'batt',0.1000000000000000055,'','');
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
INSERT INTO TimeSegmentFraction VALUES('s1','d3',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s2','d1',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s2','d2',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s2','d3',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s1','d1',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s1','d2',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s1','d4',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s1','d5',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s2','d4',0.1000000000000000055,NULL);
INSERT INTO TimeSegmentFraction VALUES('s2','d5',0.1000000000000000055,NULL);
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO StorageDuration VALUES('electricville','batt',10.0,NULL);
CREATE TABLE StorageFraction
(   
    region TEXT,
    period INTEGER REFERENCES TimePeriod (period),
    season TEXT REFERENCES TimeSeason (season),
    tod TEXT REFERENCES TimeOfDay (tod),
    tech TEXT REFERENCES Technology (tech),
    vintage INTEGER REFERENCES TimePeriod (period),
    frac REAL,
    notes TEXT,
    PRIMARY KEY (region, period, season, tod, tech, vintage)
);
INSERT INTO StorageFraction VALUES('electricville',2025,'s1','d1','batt',2025,0.5,'');
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
CREATE TABLE MinTechInputSplit
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
CREATE TABLE MinTechInputSplitAnnual
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
CREATE TABLE MinTechOutputSplit
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
INSERT INTO TimeOfDay VALUES(1,'d1');
INSERT INTO TimeOfDay VALUES(2,'d2');
INSERT INTO TimeOfDay VALUES(3,'d3');
INSERT INTO TimeOfDay VALUES(4,'d4');
INSERT INTO TimeOfDay VALUES(5,'d5');
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
    sequence INTEGER UNIQUE,
    season   TEXT
        PRIMARY KEY
);
INSERT INTO TimeSeason VALUES(1,'s1');
INSERT INTO TimeSeason VALUES(2,'s2');
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
INSERT INTO Technology VALUES('well','r','supply','water','',0,0,0,0,0,0,0,0,'plain old water');
INSERT INTO Technology VALUES('bulbs','p','residential','electric','',0,0,0,0,0,0,0,0,' residential lighting');
INSERT INTO Technology VALUES('EH','pb','electric','hydro','',0,0,0,0,0,0,0,0,'hydro power electric plant');
INSERT INTO Technology VALUES('batt','ps','electric','electric','',0,0,0,0,0,0,0,0,'big battery');
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
COMMIT;
