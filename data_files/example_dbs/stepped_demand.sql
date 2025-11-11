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
INSERT INTO MetaData VALUES('days_per_period', 365, 'count of days in each period');
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in loan_rate table');
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
CREATE TABLE SeasonLabel
(
    season TEXT PRIMARY KEY,
    notes  TEXT
);
INSERT INTO SeasonLabel VALUES('inter',NULL);
INSERT INTO SeasonLabel VALUES('summer',NULL);
INSERT INTO SeasonLabel VALUES('winter',NULL);
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
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
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
CREATE TABLE capacity_factor_tech
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
INSERT INTO capacity_factor_tech VALUES('electricville',2000,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2000,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2000,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2000,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2000,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2000,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2005,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2005,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2005,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2005,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2005,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2005,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2010,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2010,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2010,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2010,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2010,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2010,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2015,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2015,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2015,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2015,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2015,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2015,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2020,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2020,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2020,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2020,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2020,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2020,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2025,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2025,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2025,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2025,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2025,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2025,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2030,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2030,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2030,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2030,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2030,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2030,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2035,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2035,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2035,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2035,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2035,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2035,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2040,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2040,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2040,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2040,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2040,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2040,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2045,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2045,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2045,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2045,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2045,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2045,'summer','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2050,'inter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2050,'winter','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2050,'summer','day','EF',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2050,'inter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2050,'winter','day','EH',1.0,'');
INSERT INTO capacity_factor_tech VALUES('electricville',2050,'summer','day','EH',1.0,'');
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
INSERT INTO CommodityType VALUES('w','waste commodity');
INSERT INTO CommodityType VALUES('wa','waste annual commodity');
INSERT INTO CommodityType VALUES('wp','waste physical commodity');
INSERT INTO CommodityType VALUES('a','annual commodity');
INSERT INTO CommodityType VALUES('s','source commodity');
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
CREATE TABLE construction_input
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
CREATE TABLE cost_emission
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
CREATE TABLE cost_fixed
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
INSERT INTO cost_fixed VALUES('electricville',2000,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2005,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2010,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2015,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2020,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2025,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2035,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2040,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2045,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2050,'EH',1995,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2010,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2015,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2020,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2025,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2030,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2035,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2040,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2045,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2050,'EF',2010,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2000,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2005,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2010,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2015,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2020,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2025,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2030,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2035,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2040,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2045,'EH',2000,2.0,'','');
INSERT INTO cost_fixed VALUES('electricville',2050,'EH',2000,2.0,'','');
CREATE TABLE cost_invest
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
INSERT INTO cost_invest VALUES('electricville','EF',2010,200.0,'','');
INSERT INTO cost_invest VALUES('electricville','EH',2000,100.0,'','');
CREATE TABLE cost_variable
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
INSERT INTO cost_variable VALUES('electricville',2010,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2015,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2020,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2025,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2030,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2035,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2040,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2045,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2050,'EF',2010,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2000,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2005,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2010,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2015,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2020,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2025,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2030,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2035,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2040,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2045,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2050,'EH',1995,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2000,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2005,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2010,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2015,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2020,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2025,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2030,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2035,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2040,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2045,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2050,'EH',2000,2.0,'','');
INSERT INTO cost_variable VALUES('electricville',2000,'well',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('electricville',2010,'well',2000,1.0,NULL,NULL);
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
INSERT INTO DemandSpecificDistribution VALUES('electricville',2000,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2000,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2000,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2005,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2005,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2005,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2010,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2010,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2010,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2015,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2015,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2015,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2020,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2020,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2020,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2025,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2025,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2025,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2030,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2030,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2030,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2035,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2035,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2035,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2040,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2040,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2040,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2045,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2045,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2045,'winter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2050,'inter','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2050,'summer','day','RL',0.3332999999999999852,'');
INSERT INTO DemandSpecificDistribution VALUES('electricville',2050,'winter','day','RL',0.3332999999999999852,'');
CREATE TABLE end_of_life_output
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
CREATE TABLE efficiency
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
INSERT INTO efficiency VALUES('electricville','HYD','EH',1995,'ELC',1.0,'est');
INSERT INTO efficiency VALUES('electricville','HYD','EH',2000,'ELC',1.0,'est');
INSERT INTO efficiency VALUES('electricville','HYD','EF',2010,'ELC',10.0,'est');
INSERT INTO efficiency VALUES('electricville','ELC','bulbs',2000,'RL',1.0,NULL);
INSERT INTO efficiency VALUES('electricville','earth','well',2000,'HYD',1.0,'water source');
INSERT INTO efficiency VALUES('electricville','HYD','EH',2020,'ELC',1.0,NULL);
CREATE TABLE efficiency_variable
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
CREATE TABLE emission_activity
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
INSERT INTO emission_activity VALUES('electricville','co2','HYD','EH',1995,'ELC',0.05000000000000000277,'','');
INSERT INTO emission_activity VALUES('electricville','co2','HYD','EF',2010,'ELC',0.0100000000000000002,'','');
INSERT INTO emission_activity VALUES('electricville','co2','HYD','EH',2000,'ELC',0.02000000000000000041,NULL,NULL);
CREATE TABLE emission_embodied
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
CREATE TABLE emission_end_of_life
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
CREATE TABLE existing_capacity
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
INSERT INTO existing_capacity VALUES('electricville','EH',1995,0.5,'','');
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
INSERT INTO TechGroup VALUES('RPS_global','');
INSERT INTO TechGroup VALUES('RPS_common','');
CREATE TABLE loan_lifetime_process
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
INSERT INTO loan_lifetime_process VALUES('electricville','EF',2010,50.0,'');
CREATE TABLE loan_rate
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
CREATE TABLE lifetime_process
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
INSERT INTO lifetime_process VALUES('electricville','EH',1995,80.0,'#forexistingcap');
CREATE TABLE lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO lifetime_tech VALUES('electricville','EH',100.0,'');
INSERT INTO lifetime_tech VALUES('electricville','EF',100.0,'');
INSERT INTO lifetime_tech VALUES('electricville','bulbs',100.0,'super LED!');
INSERT INTO lifetime_tech VALUES('electricville','well',100.0,NULL);
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
CREATE TABLE limit_activity
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
CREATE TABLE limit_activity_share
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
CREATE TABLE limit_annual_capacity_factor
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
CREATE TABLE limit_capacity
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
INSERT INTO limit_capacity VALUES('electricville',2000,'EH','ge',0.2000000000000000111,'','');
INSERT INTO limit_capacity VALUES('electricville',2005,'EH','ge',0.2000000000000000111,'','');
INSERT INTO limit_capacity VALUES('electricville',2010,'EH','ge',0.2000000000000000111,'','');
INSERT INTO limit_capacity VALUES('electricville',2015,'EH','ge',0.2000000000000000111,'','');
INSERT INTO limit_capacity VALUES('electricville',2000,'EH','le',5.0,'','');
INSERT INTO limit_capacity VALUES('electricville',2005,'EH','le',5.0,'','');
INSERT INTO limit_capacity VALUES('electricville',2010,'EH','le',5.0,'','');
INSERT INTO limit_capacity VALUES('electricville',2015,'EH','le',5.0,'','');
INSERT INTO limit_capacity VALUES('electricville',2020,'EH','le',5.0,'','');
INSERT INTO limit_capacity VALUES('electricville',2025,'EH','le',5.0,'','');
INSERT INTO limit_capacity VALUES('electricville',2030,'EH','le',5.0,'','');
CREATE TABLE limit_capacity_share
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
CREATE TABLE limit_new_capacity
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
CREATE TABLE limit_new_capacity_share
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
CREATE TABLE limit_tech_input_split
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
CREATE TABLE limit_tech_input_split_annual
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
CREATE TABLE limit_tech_output_split
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
CREATE TABLE limit_tech_output_split_annual
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
CREATE TABLE limit_emission
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
CREATE TABLE planning_reserve_margin
(
    region TEXT
        PRIMARY KEY
        REFERENCES Region (region),
    margin REAL,
    notes TEXT
);
CREATE TABLE ramp_down_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE ramp_up_hourly
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
INSERT INTO Region VALUES('electricville',NULL);
CREATE TABLE reserve_capacity_derate
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
INSERT INTO TimeSegmentFraction VALUES(2000,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2000,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2000,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2005,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2005,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2005,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2010,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2010,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2010,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2015,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2015,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2015,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2020,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2020,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2020,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2025,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2025,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2025,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2030,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2030,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2030,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2035,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2035,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2035,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2040,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2040,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2040,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2045,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2045,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2045,'winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES(2050,'inter','day',0.3332999999999999852,'# I-D');
INSERT INTO TimeSegmentFraction VALUES(2050,'summer','day',0.3332999999999999852,'# S-D');
INSERT INTO TimeSegmentFraction VALUES(2050,'winter','day',0.3332999999999999852,'# W-D');
CREATE TABLE storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE lifetime_survival_curve
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
INSERT INTO TechnologyType VALUES('p','production technology');
INSERT INTO TechnologyType VALUES('pb','baseload production technology');
INSERT INTO TechnologyType VALUES('ps','storage production technology');
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
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    season TEXT
        REFERENCES SeasonLabel (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
INSERT INTO TimeSeason VALUES(2000,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2000,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2000,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2005,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2005,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2005,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2010,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2010,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2010,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2015,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2015,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2015,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2020,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2020,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2020,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2025,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2025,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2025,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2030,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2030,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2030,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2035,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2035,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2035,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2040,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2040,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2040,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2045,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2045,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2045,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2050,1,'inter',NULL);
INSERT INTO TimeSeason VALUES(2050,2,'summer',NULL);
INSERT INTO TimeSeason VALUES(2050,3,'winter',NULL);
CREATE TABLE time_season_sequential
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
INSERT INTO Technology VALUES('well','p','supply','water','',1,0,0,0,0,0,0,'plain old water');
INSERT INTO Technology VALUES('bulbs','p','residential','electric','',1,0,0,0,0,0,0,' residential lighting');
INSERT INTO Technology VALUES('EH','p','electric','hydro','',0,0,0,0,0,0,0,'hydro power electric plant');
INSERT INTO Technology VALUES('EF','p','electric','electric','',0,0,0,0,0,0,0,'fusion plant');
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
