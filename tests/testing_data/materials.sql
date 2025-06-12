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
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('global_discount_rate',0.05000000000000000277,'Discount Rate for future costs');
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in LoanRate table');
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
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2000,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2010,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionA',2020,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2000,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2010,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO CapacityFactorTech VALUES('RegionB',2020,'spring','overnight','SOL_PV',0.0,NULL);
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
INSERT INTO Commodity VALUES('ethos','s','import dummy source');
INSERT INTO Commodity VALUES('electricity','p','grid electricity');
INSERT INTO Commodity VALUES('passenger_km','d','demand for passenger km');
INSERT INTO Commodity VALUES('battery_nmc','a','battery - lithium nickel manganese cobalt oxide');
INSERT INTO Commodity VALUES('battery_lfp','a','battery - lithium iron phosphate');
INSERT INTO Commodity VALUES('lithium','a','lithium');
INSERT INTO Commodity VALUES('cobalt','a','cobalt');
INSERT INTO Commodity VALUES('phosphorous','a','phosphorous');
INSERT INTO Commodity VALUES('diesel','a','diesel');
INSERT INTO Commodity VALUES('heating','d','demand for residential heating');
INSERT INTO Commodity VALUES('nickel','a','nickel');
INSERT INTO Commodity VALUES('used_batt_nmc','wa','used battery - lithium nickel manganese cobalt oxide');
INSERT INTO Commodity VALUES('used_batt_lfp','wa','used battery - lithium iron phosphate');
INSERT INTO Commodity VALUES('co2e','e','emitted co2-equivalent GHGs');
INSERT INTO Commodity VALUES('waste_steel','w','waste steel from cars');
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
INSERT INTO ConstructionInput VALUES('RegionA','battery_nmc','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionA','battery_lfp','CAR_PHEV',2000,0.1000000000000000055,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionA','battery_nmc','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionA','battery_lfp','CAR_PHEV',2010,0.1000000000000000055,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionA','battery_nmc','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionA','battery_lfp','CAR_PHEV',2020,0.1000000000000000055,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionB','battery_nmc','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionB','battery_lfp','CAR_PHEV',2000,0.1000000000000000055,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionB','battery_nmc','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionB','battery_lfp','CAR_PHEV',2010,0.1000000000000000055,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionB','battery_nmc','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO ConstructionInput VALUES('RegionB','battery_lfp','CAR_PHEV',2020,0.1000000000000000055,NULL,NULL);
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
INSERT INTO CostEmission VALUES('RegionA',2000,'co2e',1.0,NULL,NULL);
INSERT INTO CostEmission VALUES('RegionA',2010,'co2e',1.0,NULL,NULL);
INSERT INTO CostEmission VALUES('RegionA',2020,'co2e',1.0,NULL,NULL);
INSERT INTO CostEmission VALUES('RegionB',2000,'co2e',1.0,NULL,NULL);
INSERT INTO CostEmission VALUES('RegionB',2010,'co2e',1.0,NULL,NULL);
INSERT INTO CostEmission VALUES('RegionB',2020,'co2e',1.0,NULL,NULL);
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
INSERT INTO CostInvest VALUES('RegionA','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_PHEV',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_PHEV',2010,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_PHEV',2020,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_ICE',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_ICE',2010,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','CAR_ICE',2020,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','RECYCLE_NMC',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','RECYCLE_LFP',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','MANUFAC_NMC',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','MANUFAC_LFP',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','BATT_GRID',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','SOL_PV',2000,10.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA','GEN_DSL',2000,2.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_PHEV',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_PHEV',2010,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_PHEV',2020,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_ICE',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_ICE',2010,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','CAR_ICE',2020,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','RECYCLE_NMC',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','RECYCLE_LFP',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','MANUFAC_NMC',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','MANUFAC_LFP',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','BATT_GRID',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','GEN_DSL',2000,2.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionA-RegionB','ELEC_INTERTIE',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB-RegionA','ELEC_INTERTIE',2000,1.0,NULL,NULL);
INSERT INTO CostInvest VALUES('RegionB','SOL_PV',2000,1.0,NULL,NULL);
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
INSERT INTO CostVariable VALUES('RegionA',2000,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2010,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2020,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2000,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2010,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2020,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2000,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2010,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2020,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2000,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2010,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2020,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2000,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2010,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2020,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2000,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2010,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionA',2020,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2000,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2010,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2020,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2000,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2010,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2020,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2000,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2010,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2020,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2000,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2010,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2020,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2000,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2010,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2020,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2000,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2010,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO CostVariable VALUES('RegionB',2020,'DOMESTIC_NI',2000,0.5,NULL,NULL);
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
INSERT INTO Demand VALUES('RegionA',2000,'passenger_km',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionA',2010,'passenger_km',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionA',2020,'passenger_km',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionA',2000,'heating',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionA',2010,'heating',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionA',2020,'heating',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionB',2000,'passenger_km',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionB',2010,'passenger_km',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionB',2020,'passenger_km',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionB',2000,'heating',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionB',2010,'heating',1.0,NULL,NULL);
INSERT INTO Demand VALUES('RegionB',2020,'heating',1.0,NULL,NULL);
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
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'summer','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'spring','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'summer','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'spring','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'summer','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'spring','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'summer','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2000,'spring','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'summer','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'spring','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'summer','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'spring','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'summer','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'spring','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'summer','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2010,'spring','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'summer','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'spring','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'summer','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'spring','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'summer','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'spring','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'summer','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionA',2020,'spring','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'summer','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'spring','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'summer','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'spring','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'summer','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'spring','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'summer','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2000,'spring','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'summer','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'spring','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'summer','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'spring','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'summer','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'spring','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'summer','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2010,'spring','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'summer','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'spring','morning','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'summer','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'spring','afternoon','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'summer','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'spring','evening','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'summer','overnight','heating',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO DemandSpecificDistribution VALUES('RegionB',2020,'spring','overnight','heating',0.0,NULL);
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
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_BEV',1990,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_PHEV',1990,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_BEV',2000,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_PHEV',2000,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_BEV',2010,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_PHEV',2010,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_BEV',1990,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_PHEV',1990,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_BEV',2000,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_PHEV',2000,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_BEV',2010,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_PHEV',2010,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_BEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_ICE',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_PHEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_BEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_ICE',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_PHEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_BEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_ICE',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionA','CAR_PHEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_BEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_ICE',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_PHEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_BEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_ICE',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_PHEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_BEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_ICE',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO EndOfLifeOutput VALUES('RegionB','CAR_PHEV',2010,'waste_steel',1.0,NULL,NULL);
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
INSERT INTO Efficiency VALUES('RegionA','ethos','DOMESTIC_NI',2000,'nickel',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','ethos','IMPORT_LI',2000,'lithium',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','ethos','IMPORT_NI',2000,'nickel',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','ethos','IMPORT_CO',2000,'cobalt',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','ethos','IMPORT_P',2000,'phosphorous',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','used_batt_nmc','RECYCLE_NMC',2000,'battery_nmc',0.2000000000000000111,NULL);
INSERT INTO Efficiency VALUES('RegionA','used_batt_lfp','RECYCLE_LFP',2000,'battery_lfp',0.2000000000000000111,NULL);
INSERT INTO Efficiency VALUES('RegionA','lithium','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','nickel','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','cobalt','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','lithium','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','phosphorous','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','RECYCLE_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionA','electricity','RECYCLE_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionA','electricity','MANUFAC_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionA','electricity','MANUFAC_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionA','diesel','GEN_DSL',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','ethos','SOL_PV',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','BATT_GRID',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','FURNACE',2000,'heating',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','HEATPUMP',2000,'heating',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_BEV',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_ICE',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_BEV',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_ICE',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_BEV',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_ICE',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_BEV',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','electricity','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA','diesel','CAR_ICE',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','DOMESTIC_NI',2000,'nickel',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','IMPORT_LI',2000,'lithium',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','IMPORT_NI',2000,'nickel',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','IMPORT_CO',2000,'cobalt',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','IMPORT_P',2000,'phosphorous',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','used_batt_nmc','RECYCLE_NMC',2000,'battery_nmc',0.2000000000000000111,NULL);
INSERT INTO Efficiency VALUES('RegionB','used_batt_lfp','RECYCLE_LFP',2000,'battery_lfp',0.2000000000000000111,NULL);
INSERT INTO Efficiency VALUES('RegionB','lithium','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','nickel','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','cobalt','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','lithium','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','phosphorous','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','RECYCLE_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionB','electricity','RECYCLE_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionB','electricity','MANUFAC_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionB','electricity','MANUFAC_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO Efficiency VALUES('RegionB','diesel','GEN_DSL',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','SOL_PV',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','BATT_GRID',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','FURNACE',2000,'heating',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','HEATPUMP',2000,'heating',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_BEV',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_ICE',1990,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_BEV',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_ICE',2000,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_BEV',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_ICE',2010,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_BEV',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','electricity','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionB','diesel','CAR_ICE',2020,'passenger_km',1.0,NULL);
INSERT INTO Efficiency VALUES('RegionA-RegionB','electricity','ELEC_INTERTIE',2000,'electricity',0.9000000000000000222,NULL);
INSERT INTO Efficiency VALUES('RegionB-RegionA','electricity','ELEC_INTERTIE',2000,'electricity',0.9000000000000000222,NULL);
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
INSERT INTO EmissionActivity VALUES('RegionA','co2e','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL,'assumed combusted');
INSERT INTO EmissionActivity VALUES('RegionB','co2e','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL,'assumed combusted');
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
INSERT INTO ExistingCapacity VALUES('RegionA','CAR_BEV',1990,1.0,NULL,NULL);
INSERT INTO ExistingCapacity VALUES('RegionA','CAR_PHEV',1990,1.0,NULL,NULL);
INSERT INTO ExistingCapacity VALUES('RegionA','CAR_ICE',1990,1.0,NULL,NULL);
INSERT INTO ExistingCapacity VALUES('RegionB','CAR_BEV',1990,1.0,NULL,NULL);
INSERT INTO ExistingCapacity VALUES('RegionB','CAR_PHEV',1990,1.0,NULL,NULL);
INSERT INTO ExistingCapacity VALUES('RegionB','CAR_ICE',1990,1.0,NULL,NULL);
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
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
INSERT INTO LifetimeTech VALUES('RegionA','CAR_BEV',10.0,NULL);
INSERT INTO LifetimeTech VALUES('RegionA','CAR_PHEV',10.0,NULL);
INSERT INTO LifetimeTech VALUES('RegionA','CAR_ICE',10.0,NULL);
INSERT INTO LifetimeTech VALUES('RegionB','CAR_BEV',10.0,NULL);
INSERT INTO LifetimeTech VALUES('RegionB','CAR_PHEV',10.0,NULL);
INSERT INTO LifetimeTech VALUES('RegionB','CAR_ICE',10.0,NULL);
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
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2000,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2010,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionA',2020,'diesel','CAR_PHEV','le',0.8000000000000000444,NULL);
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2000,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2010,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO LimitTechInputSplitAnnual VALUES('RegionB',2020,'diesel','CAR_PHEV','le',0.8000000000000000444,NULL);
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
INSERT INTO Region VALUES('RegionA',NULL);
INSERT INTO Region VALUES('RegionB',NULL);
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
INSERT INTO TimeSegmentFraction VALUES(2000,'summer','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'autumn','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'winter','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'spring','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'summer','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'autumn','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'winter','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'spring','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'summer','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'autumn','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'winter','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'spring','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'summer','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'autumn','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'winter','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'spring','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'summer','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'autumn','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'winter','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'spring','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'summer','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'autumn','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'winter','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'spring','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'summer','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'autumn','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'winter','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'spring','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'summer','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'autumn','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'winter','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2010,'spring','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'summer','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'autumn','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'winter','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'spring','morning',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'summer','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'autumn','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'winter','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'spring','afternoon',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'summer','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'autumn','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'winter','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'spring','evening',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'summer','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'autumn','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'winter','overnight',0.0625,NULL);
INSERT INTO TimeSegmentFraction VALUES(2020,'spring','overnight',0.0625,NULL);
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO StorageDuration VALUES('RegionA','BATT_GRID',2.0,'2 hours energy storage');
INSERT INTO StorageDuration VALUES('RegionB','BATT_GRID',2.0,'2 hours energy storage');
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
INSERT INTO TimeOfDay VALUES(1,'morning');
INSERT INTO TimeOfDay VALUES(2,'afternoon');
INSERT INTO TimeOfDay VALUES(3,'evening');
INSERT INTO TimeOfDay VALUES(4,'overnight');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(1,1990,'e');
INSERT INTO TimePeriod VALUES(2,2000,'f');
INSERT INTO TimePeriod VALUES(3,2010,'f');
INSERT INTO TimePeriod VALUES(4,2020,'f');
INSERT INTO TimePeriod VALUES(5,2030,'f');
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
INSERT INTO TimeSeason VALUES(2000,1,'summer',NULL);
INSERT INTO TimeSeason VALUES(2000,2,'autumn',NULL);
INSERT INTO TimeSeason VALUES(2000,3,'winter',NULL);
INSERT INTO TimeSeason VALUES(2000,4,'spring',NULL);
INSERT INTO TimeSeason VALUES(2010,5,'summer',NULL);
INSERT INTO TimeSeason VALUES(2010,6,'autumn',NULL);
INSERT INTO TimeSeason VALUES(2010,7,'winter',NULL);
INSERT INTO TimeSeason VALUES(2010,8,'spring',NULL);
INSERT INTO TimeSeason VALUES(2020,9,'summer',NULL);
INSERT INTO TimeSeason VALUES(2020,10,'autumn',NULL);
INSERT INTO TimeSeason VALUES(2020,11,'winter',NULL);
INSERT INTO TimeSeason VALUES(2020,12,'spring',NULL);
CREATE TABLE IF NOT EXISTS TimeStorageSeason
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    storage_season TEXT,
    season TEXT
        REFERENCES TimeSeason (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, storage_season, season)
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
INSERT INTO Technology VALUES('IMPORT_LI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'lithium importer');
INSERT INTO Technology VALUES('IMPORT_CO','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'cobalt importer');
INSERT INTO Technology VALUES('IMPORT_P','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'phosphorous importer');
INSERT INTO Technology VALUES('CAR_BEV','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - battery electric');
INSERT INTO Technology VALUES('CAR_PHEV','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - plug in hybrid');
INSERT INTO Technology VALUES('CAR_ICE','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - internal combustion');
INSERT INTO Technology VALUES('RECYCLE_NMC','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'nmc battery recycler');
INSERT INTO Technology VALUES('RECYCLE_LFP','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'lfp battery recycler');
INSERT INTO Technology VALUES('MANUFAC_NMC','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'nmc battery manufacturing');
INSERT INTO Technology VALUES('MANUFAC_LFP','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'lfp battery manufacturing');
INSERT INTO Technology VALUES('IMPORT_NI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'nickel importer');
INSERT INTO Technology VALUES('DOMESTIC_NI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'domestic nickel production');
INSERT INTO Technology VALUES('GEN_DSL','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,'diesel generators');
INSERT INTO Technology VALUES('SOL_PV','p','electricity',NULL,NULL,0,0,0,1,0,0,0,0,'solar panels');
INSERT INTO Technology VALUES('BATT_GRID','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,0,'grid battery storage');
INSERT INTO Technology VALUES('FURNACE','p','residential',NULL,NULL,1,0,0,0,0,0,0,0,'diesel furnace heater');
INSERT INTO Technology VALUES('HEATPUMP','p','residential',NULL,NULL,1,0,0,0,0,0,0,0,'heat pump');
INSERT INTO Technology VALUES('IMPORT_DSL','p','fuels',NULL,NULL,1,1,0,0,0,0,0,0,'diesel importer');
INSERT INTO Technology VALUES('ELEC_INTERTIE','p','electricity',NULL,NULL,0,0,0,0,0,0,1,0,'dummy tech to make landfill feasible');
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
