PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE MetaData
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
INSERT INTO MetaData VALUES('myopic_base_year',2000,'Base Year for Myopic Analysis');
INSERT INTO MetaData VALUES('DB_MAJOR',3,'DB major version number');
INSERT INTO MetaData VALUES('DB_MINOR',1,'DB minor version number');
INSERT INTO MetaData VALUES('link_seasons',1,'Carry storage states between seasons');
INSERT INTO MetaData VALUES('state_sequencing',0,'0 = loop periods, 1 = loop seasons');
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
CREATE TABLE SectorLabel
(
    sector TEXT,
    PRIMARY KEY (sector)
);
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
INSERT INTO CapacityFactorTech VALUES('TestRegion',2000,'S1','TOD1','TechCurtailment',1.0,NULL);
INSERT INTO CapacityFactorTech VALUES('TestRegion',2000,'S1','TOD2','TechCurtailment',0.5,NULL);
INSERT INTO CapacityFactorTech VALUES('TestRegion',2000,'S1','TOD1','TechOrdinary',1.0,NULL);
INSERT INTO CapacityFactorTech VALUES('TestRegion',2000,'S1','TOD2','TechOrdinary',0.5,NULL);
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
INSERT INTO Commodity VALUES('annual_in','s',NULL);
INSERT INTO Commodity VALUES('flex_in','s',NULL);
INSERT INTO Commodity VALUES('ordinary_in','s',NULL);
INSERT INTO Commodity VALUES('curtailment_in','s',NULL);
INSERT INTO Commodity VALUES('annual_out','d',NULL);
INSERT INTO Commodity VALUES('flex_out','p',NULL);
INSERT INTO Commodity VALUES('ordinary_out','d',NULL);
INSERT INTO Commodity VALUES('curtailment_out','d',NULL);
INSERT INTO Commodity VALUES('emission','e',NULL);
INSERT INTO Commodity VALUES('flex_null','d',NULL);
INSERT INTO Commodity VALUES('annual_flex_out','p',NULL);
INSERT INTO Commodity VALUES('annual_flex_in','s',NULL);
INSERT INTO Commodity VALUES('annual_flex_null','d',NULL);
INSERT INTO Commodity VALUES('embodied_in','s',NULL);
INSERT INTO Commodity VALUES('embodied_out','d',NULL);
INSERT INTO Commodity VALUES('eol_in','s',NULL);
INSERT INTO Commodity VALUES('eol_out','d',NULL);
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
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
INSERT INTO CostEmission VALUES('TestRegion',2000,'emission',0.7,NULL,NULL);
INSERT INTO CostEmission VALUES('TestRegion',2005,'emission',0.7,NULL,NULL);
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
INSERT INTO Demand VALUES('TestRegion',2000,'annual_out',1.0,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2000,'ordinary_out',0.3,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2000,'curtailment_out',0.3,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2000,'flex_null',0.3,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2000,'annual_flex_null',0.3,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2000,'embodied_out',0.6,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2000,'eol_out',0.6,NULL,NULL);
INSERT INTO Demand VALUES('TestRegion',2005,'ordinary_out',0.3,NULL,NULL);
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
INSERT INTO Efficiency VALUES('TestRegion','annual_in','TechAnnual',2000,'annual_out',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','flex_in','TechFlex',2000,'flex_out',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','ordinary_in','TechOrdinary',2000,'ordinary_out',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','curtailment_in','TechCurtailment',2000,'curtailment_out',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','flex_out','TechFlexNull',2000,'flex_null',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','annual_flex_out','TechFlexNull',2000,'annual_flex_null',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','annual_flex_in','TechAnnualFlex',2000,'annual_flex_out',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','embodied_in','TechEmbodied',2000,'embodied_out',1.0,NULL);
INSERT INTO Efficiency VALUES('TestRegion','eol_in','TechEndOfLife',2000,'eol_out',1.0,NULL);
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
INSERT INTO EmissionActivity VALUES('TestRegion','emission','annual_in','TechAnnual',2000,'annual_out',1.0,NULL,NULL);
INSERT INTO EmissionActivity VALUES('TestRegion','emission','flex_in','TechFlex',2000,'flex_out',1.0,NULL,NULL);
INSERT INTO EmissionActivity VALUES('TestRegion','emission','ordinary_in','TechOrdinary',2000,'ordinary_out',1.0,NULL,NULL);
INSERT INTO EmissionActivity VALUES('TestRegion','emission','curtailment_in','TechCurtailment',2000,'curtailment_out',1.0,NULL,NULL);
INSERT INTO EmissionActivity VALUES('TestRegion','emission','annual_flex_in','TechAnnualFlex',2000,'annual_flex_out',1.0,NULL,NULL);
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
INSERT INTO EmissionEmbodied VALUES('TestRegion','emission','TechEmbodied',2000,0.5,NULL,NULL);
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
INSERT INTO EmissionEndOfLife VALUES('TestRegion','emission','TechEndOfLife',2000,0.5,NULL,NULL);
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
INSERT INTO LifetimeTech VALUES('TestRegion','TechEndOfLife',5,NULL);
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
INSERT INTO MaxActivity VALUES('TestRegion',2000,'TechFlex',1.0,NULL,NULL);
INSERT INTO MaxActivity VALUES('TestRegion',2000,'TechAnnualFlex',1.0,NULL,NULL);
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
INSERT INTO MaxCapacity VALUES('TestRegion',2000,'TechOrdinary',1.0,NULL,NULL);
INSERT INTO MaxCapacity VALUES('TestRegion',2000,'TechCurtailment',1.0,NULL,NULL);
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
INSERT INTO MinActivity VALUES('TestRegion',2000,'TechFlex',1.0,NULL,NULL);
INSERT INTO MinActivity VALUES('TestRegion',2000,'TechAnnualFlex',1.0,NULL,NULL);
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
INSERT INTO MinCapacity VALUES('TestRegion',2000,'TechOrdinary',1.0,NULL,NULL);
INSERT INTO MinCapacity VALUES('TestRegion',2000,'TechCurtailment',1.0,NULL,NULL);
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
        REFERENCES TimePeriod (period),
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
INSERT INTO Region VALUES('TestRegion',NULL);
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
INSERT INTO TimeSegmentFraction VALUES(2000,'S1','TOD1',0.5,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'S1','TOD2',0.5,NULL);
INSERT INTO TimeSegmentFraction VALUES(2005,'S1','TOD1',0.5,NULL);
INSERT INTO TimeSegmentFraction VALUES(2005,'S1','TOD2',0.5,NULL);
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE StorageLevelFraction
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
    fraction REAL,
    notes    TEXT,
    PRIMARY KEY(region, period, season, tod, tech, vintage)
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
CREATE TABLE MinTechOutputSplitAnnual
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
CREATE TABLE MaxTechInputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech)
);
CREATE TABLE MaxTechInputSplitAnnual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech)
);
CREATE TABLE MaxTechOutputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm)
);
CREATE TABLE MaxTechOutputSplitAnnual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm)
);
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(1,'TOD1');
INSERT INTO TimeOfDay VALUES(2,'TOD2');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(1,1999,'e');
INSERT INTO TimePeriod VALUES(2,2000,'f');
INSERT INTO TimePeriod VALUES(3,2005,'f');
INSERT INTO TimePeriod VALUES(4,2010,'f');
CREATE TABLE TimeSeason
(
    season TEXT
        PRIMARY KEY
);
INSERT INTO TimeSeason VALUES('S1');
CREATE TABLE PeriodSeasons
(   
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    season TEXT
        REFERENCES TimeSeason (season),
    notes TEXT,
    PRIMARY KEY (period, sequence)
);
INSERT INTO PeriodSeasons VALUES(2000,1,'S1',NULL);
INSERT INTO PeriodSeasons VALUES(2005,1,'S1',NULL);
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
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinNewCapacityGroupShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT
        REFERENCES TechGroup (group_name),
    super_group    TEXT
        REFERENCES TechGroup (group_name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group)
);
CREATE TABLE MaxNewCapacityGroupShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT
        REFERENCES TechGroup (group_name),
    super_group    TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group)
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
CREATE TABLE IF NOT EXISTS "MinSeasonalActivity"
(
	"region"    TEXT
        REFERENCES Region (region),
	"period"	INTEGER
        REFERENCES TimePeriod (period),
	"season"	TEXT
        REFERENCES TimeSeason (season),
	"tech"      TEXT
        REFERENCES Technology (tech),
	"min_act"	REAL,
	"units"	TEXT,
	"notes"	TEXT,
	PRIMARY KEY("region","period","season","tech")
);
CREATE TABLE IF NOT EXISTS "MaxSeasonalActivity"
(
	"region"    TEXT
        REFERENCES Region (region),
	"period"	INTEGER
        REFERENCES TimePeriod (period),
	"season"	TEXT
        REFERENCES TimeSeason (season),
	"tech"      TEXT
        REFERENCES Technology (tech),
	"max_act"	REAL,
	"units"	TEXT,
	"notes"	TEXT,
	PRIMARY KEY("region","period","season","tech")
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
    description  TEXT,
    FOREIGN KEY (flag) REFERENCES TechnologyType (label)
);
INSERT INTO Technology VALUES('TechAnnual','p','energy',NULL,NULL,0,1,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('TechFlex','p','energy',NULL,NULL,0,0,0,0,0,1,0,NULL);
INSERT INTO Technology VALUES('TechOrdinary','p','energy',NULL,NULL,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('TechCurtailment','p','energy',NULL,NULL,0,0,0,1,0,0,0,NULL);
INSERT INTO Technology VALUES('TechFlexNull','p','energy',NULL,NULL,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('TechAnnualFlex','p','energy',NULL,NULL,0,1,0,0,0,1,0,NULL);
INSERT INTO Technology VALUES('TechEmbodied','p','energy',NULL,NULL,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('TechEndOfLife','p','energy',NULL,NULL,0,0,0,0,0,0,0,NULL);
CREATE TABLE OutputCost
(
    scenario TEXT,
    region   TEXT REFERENCES Region (region),
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
