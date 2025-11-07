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
INSERT INTO metadata VALUES ('days_per_period', 365, 'count of days in each period');
CREATE TABLE metadata_real
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO metadata_real VALUES('global_discount_rate',0.05000000000000000277,'Discount Rate for future costs');
INSERT INTO metadata_real VALUES('default_loan_rate',0.05000000000000000277,'Default Loan Rate if not specified in loan_rate table');
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
INSERT INTO SeasonLabel VALUES('summer',NULL);
INSERT INTO SeasonLabel VALUES('autumn',NULL);
INSERT INTO SeasonLabel VALUES('winter',NULL);
INSERT INTO SeasonLabel VALUES('spring',NULL);
CREATE TABLE SectorLabel
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
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
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2000,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2010,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionA',2020,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2000,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2010,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'summer','morning','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'autumn','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'winter','morning','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'spring','morning','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'summer','afternoon','SOL_PV',0.2999999999999999889,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'autumn','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'winter','afternoon','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'spring','afternoon','SOL_PV',0.2000000000000000111,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'summer','evening','SOL_PV',0.1000000000000000055,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO capacity_factor_tech VALUES('regionB',2020,'spring','overnight','SOL_PV',0.0,NULL);
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES commodityType (label),
    description TEXT
);
INSERT INTO commodity VALUES('ethos','s','import dummy source');
INSERT INTO commodity VALUES('electricity','p','grid electricity');
INSERT INTO commodity VALUES('passenger_km','d','demand for passenger km');
INSERT INTO commodity VALUES('battery_nmc','a','battery - lithium nickel manganese cobalt oxide');
INSERT INTO commodity VALUES('battery_lfp','a','battery - lithium iron phosphate');
INSERT INTO commodity VALUES('lithium','a','lithium');
INSERT INTO commodity VALUES('cobalt','a','cobalt');
INSERT INTO commodity VALUES('phosphorous','a','phosphorous');
INSERT INTO commodity VALUES('diesel','a','diesel');
INSERT INTO commodity VALUES('heating','d','demand for residential heating');
INSERT INTO commodity VALUES('nickel','a','nickel');
INSERT INTO commodity VALUES('used_batt_nmc','wa','used battery - lithium nickel manganese cobalt oxide');
INSERT INTO commodity VALUES('used_batt_lfp','wa','used battery - lithium iron phosphate');
INSERT INTO commodity VALUES('co2e','e','emitted co2-equivalent GHGs');
INSERT INTO commodity VALUES('waste_steel','w','waste steel from cars');
CREATE TABLE commodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO commodityType VALUES('w','waste commodity');
INSERT INTO commodityType VALUES('wa','waste annual commodity');
INSERT INTO commodityType VALUES('wp','waste physical commodity');
INSERT INTO commodityType VALUES('a','annual commodity');
INSERT INTO commodityType VALUES('p','physical commodity');
INSERT INTO commodityType VALUES('e','emissions commodity');
INSERT INTO commodityType VALUES('d','demand commodity');
INSERT INTO commodityType VALUES('s','source commodity');
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
INSERT INTO construction_input VALUES('regionA','battery_nmc','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO construction_input VALUES('regionA','battery_lfp','CAR_PHEV',2000,0.1000000000000000055,NULL,NULL);
INSERT INTO construction_input VALUES('regionA','battery_nmc','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO construction_input VALUES('regionA','battery_lfp','CAR_PHEV',2010,0.1000000000000000055,NULL,NULL);
INSERT INTO construction_input VALUES('regionA','battery_nmc','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO construction_input VALUES('regionA','battery_lfp','CAR_PHEV',2020,0.1000000000000000055,NULL,NULL);
INSERT INTO construction_input VALUES('regionB','battery_nmc','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO construction_input VALUES('regionB','battery_lfp','CAR_PHEV',2000,0.1000000000000000055,NULL,NULL);
INSERT INTO construction_input VALUES('regionB','battery_nmc','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO construction_input VALUES('regionB','battery_lfp','CAR_PHEV',2010,0.1000000000000000055,NULL,NULL);
INSERT INTO construction_input VALUES('regionB','battery_nmc','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO construction_input VALUES('regionB','battery_lfp','CAR_PHEV',2020,0.1000000000000000055,NULL,NULL);
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
INSERT INTO cost_emission VALUES('regionA',2000,'co2e',1.0,NULL,NULL);
INSERT INTO cost_emission VALUES('regionA',2010,'co2e',1.0,NULL,NULL);
INSERT INTO cost_emission VALUES('regionA',2020,'co2e',1.0,NULL,NULL);
INSERT INTO cost_emission VALUES('regionB',2000,'co2e',1.0,NULL,NULL);
INSERT INTO cost_emission VALUES('regionB',2010,'co2e',1.0,NULL,NULL);
INSERT INTO cost_emission VALUES('regionB',2020,'co2e',1.0,NULL,NULL);
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
INSERT INTO cost_invest VALUES('regionA','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_PHEV',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_PHEV',2010,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_PHEV',2020,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_ICE',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_ICE',2010,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','CAR_ICE',2020,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','RECYCLE_NMC',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','RECYCLE_LFP',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','MANUFAC_NMC',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','MANUFAC_LFP',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','BATT_GRID',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','SOL_PV',2000,10.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA','GEN_DSL',2000,2.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_PHEV',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_PHEV',2010,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_PHEV',2020,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_ICE',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_ICE',2010,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','CAR_ICE',2020,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','RECYCLE_NMC',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','RECYCLE_LFP',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','MANUFAC_NMC',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','MANUFAC_LFP',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','BATT_GRID',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','GEN_DSL',2000,2.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionA-regionB','ELEC_INTERTIE',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB-regionA','ELEC_INTERTIE',2000,1.0,NULL,NULL);
INSERT INTO cost_invest VALUES('regionB','SOL_PV',2000,1.0,NULL,NULL);
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
INSERT INTO cost_variable VALUES('regionA',2000,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2010,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2020,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2000,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2010,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2020,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2000,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2010,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2020,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2000,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2010,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2020,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2000,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2010,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2020,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2000,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2010,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO cost_variable VALUES('regionA',2020,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2000,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2010,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2020,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2000,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2010,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2020,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2000,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2010,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2020,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2000,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2010,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2020,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2000,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2010,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2020,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2000,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2010,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO cost_variable VALUES('regionB',2020,'DOMESTIC_NI',2000,0.5,NULL,NULL);
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
INSERT INTO demand VALUES('regionA',2000,'passenger_km',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionA',2010,'passenger_km',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionA',2020,'passenger_km',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionA',2000,'heating',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionA',2010,'heating',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionA',2020,'heating',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionB',2000,'passenger_km',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionB',2010,'passenger_km',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionB',2020,'passenger_km',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionB',2000,'heating',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionB',2010,'heating',1.0,NULL,NULL);
INSERT INTO demand VALUES('regionB',2020,'heating',1.0,NULL,NULL);
CREATE TABLE demand_specific_distributionon
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
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'summer','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'spring','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'summer','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'spring','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'summer','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'spring','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'summer','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2000,'spring','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'summer','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'spring','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'summer','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'spring','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'summer','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'spring','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'summer','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2010,'spring','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'summer','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'spring','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'summer','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'spring','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'summer','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'spring','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'summer','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionA',2020,'spring','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'summer','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'spring','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'summer','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'spring','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'summer','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'spring','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'summer','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2000,'spring','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'summer','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'spring','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'summer','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'spring','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'summer','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'spring','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'summer','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2010,'spring','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'summer','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'autumn','morning','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'winter','morning','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'spring','morning','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'summer','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'autumn','afternoon','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'winter','afternoon','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'spring','afternoon','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'summer','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'autumn','evening','heating',0.08000000000000000166,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'winter','evening','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'spring','evening','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'summer','overnight','heating',0.0,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'autumn','overnight','heating',0.1199999999999999956,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'winter','overnight','heating',0.1600000000000000033,NULL);
INSERT INTO demand_specific_distributionon VALUES('regionB',2020,'spring','overnight','heating',0.0,NULL);
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
INSERT INTO end_of_life_output VALUES('regionA','CAR_BEV',1990,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_PHEV',1990,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_BEV',2000,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_PHEV',2000,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_BEV',2010,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_PHEV',2010,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_BEV',1990,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_PHEV',1990,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_BEV',2000,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_PHEV',2000,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_BEV',2010,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_PHEV',2010,'used_batt_lfp',0.1000000000000000055,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_BEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_ICE',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_PHEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_BEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_ICE',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_PHEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_BEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_ICE',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionA','CAR_PHEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_BEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_ICE',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_PHEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_BEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_ICE',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_PHEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_BEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_ICE',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO end_of_life_output VALUES('regionB','CAR_PHEV',2010,'waste_steel',1.0,NULL,NULL);
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
INSERT INTO efficiency VALUES('regionA','ethos','DOMESTIC_NI',2000,'nickel',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','ethos','IMPORT_LI',2000,'lithium',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','ethos','IMPORT_NI',2000,'nickel',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','ethos','IMPORT_CO',2000,'cobalt',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','ethos','IMPORT_P',2000,'phosphorous',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','used_batt_nmc','RECYCLE_NMC',2000,'battery_nmc',0.2000000000000000111,NULL);
INSERT INTO efficiency VALUES('regionA','used_batt_lfp','RECYCLE_LFP',2000,'battery_lfp',0.2000000000000000111,NULL);
INSERT INTO efficiency VALUES('regionA','lithium','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','nickel','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','cobalt','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','lithium','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','phosphorous','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','RECYCLE_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionA','electricity','RECYCLE_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionA','electricity','MANUFAC_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionA','electricity','MANUFAC_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionA','diesel','GEN_DSL',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','ethos','SOL_PV',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','BATT_GRID',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','FURNACE',2000,'heating',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','HEATPUMP',2000,'heating',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_BEV',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_ICE',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_BEV',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_ICE',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_BEV',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_ICE',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_BEV',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','electricity','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA','diesel','CAR_ICE',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','DOMESTIC_NI',2000,'nickel',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','IMPORT_LI',2000,'lithium',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','IMPORT_NI',2000,'nickel',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','IMPORT_CO',2000,'cobalt',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','IMPORT_P',2000,'phosphorous',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','used_batt_nmc','RECYCLE_NMC',2000,'battery_nmc',0.2000000000000000111,NULL);
INSERT INTO efficiency VALUES('regionB','used_batt_lfp','RECYCLE_LFP',2000,'battery_lfp',0.2000000000000000111,NULL);
INSERT INTO efficiency VALUES('regionB','lithium','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','nickel','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','cobalt','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','lithium','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','phosphorous','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','RECYCLE_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionB','electricity','RECYCLE_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionB','electricity','MANUFAC_NMC',2000,'battery_nmc',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionB','electricity','MANUFAC_LFP',2000,'battery_lfp',0.00100000000000000002,'Effectively zero');
INSERT INTO efficiency VALUES('regionB','diesel','GEN_DSL',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','SOL_PV',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','BATT_GRID',2000,'electricity',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','FURNACE',2000,'heating',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','HEATPUMP',2000,'heating',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_BEV',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_ICE',1990,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_BEV',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_ICE',2000,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_BEV',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_ICE',2010,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_BEV',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','electricity','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionB','diesel','CAR_ICE',2020,'passenger_km',1.0,NULL);
INSERT INTO efficiency VALUES('regionA-regionB','electricity','ELEC_INTERTIE',2000,'electricity',0.9000000000000000222,NULL);
INSERT INTO efficiency VALUES('regionB-regionA','electricity','ELEC_INTERTIE',2000,'electricity',0.9000000000000000222,NULL);
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
INSERT INTO emission_activity VALUES('regionA','co2e','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL,'assumed combusted');
INSERT INTO emission_activity VALUES('regionB','co2e','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL,'assumed combusted');
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
INSERT INTO existing_capacity VALUES('regionA','CAR_BEV',1990,1.0,NULL,NULL);
INSERT INTO existing_capacity VALUES('regionA','CAR_PHEV',1990,1.0,NULL,NULL);
INSERT INTO existing_capacity VALUES('regionA','CAR_ICE',1990,1.0,NULL,NULL);
INSERT INTO existing_capacity VALUES('regionB','CAR_BEV',1990,1.0,NULL,NULL);
INSERT INTO existing_capacity VALUES('regionB','CAR_PHEV',1990,1.0,NULL,NULL);
INSERT INTO existing_capacity VALUES('regionB','CAR_ICE',1990,1.0,NULL,NULL);
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
CREATE TABLE loan_lifetime_process
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
INSERT INTO lifetime_tech VALUES('regionA','CAR_BEV',10.0,NULL);
INSERT INTO lifetime_tech VALUES('regionA','CAR_PHEV',10.0,NULL);
INSERT INTO lifetime_tech VALUES('regionA','CAR_ICE',10.0,NULL);
INSERT INTO lifetime_tech VALUES('regionB','CAR_BEV',10.0,NULL);
INSERT INTO lifetime_tech VALUES('regionB','CAR_PHEV',10.0,NULL);
INSERT INTO lifetime_tech VALUES('regionB','CAR_ICE',10.0,NULL);
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
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2000,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2010,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionA',2020,'diesel','CAR_PHEV','le',0.8000000000000000444,NULL);
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'lithium','MANUFAC_NMC','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'nickel','MANUFAC_NMC','le',0.1499999999999999945,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'cobalt','MANUFAC_NMC','le',0.04000000000000000083,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'electricity','MANUFAC_NMC','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'lithium','MANUFAC_LFP','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'phosphorous','MANUFAC_LFP','le',0.1900000000000000022,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'electricity','MANUFAC_LFP','le',0.0100000000000000002,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2000,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2010,'diesel','CAR_PHEV','le',0.8000000000000000444,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'electricity','CAR_PHEV','le',0.2000000000000000111,'');
INSERT INTO limit_tech_input_split_annual VALUES('regionB',2020,'diesel','CAR_PHEV','le',0.8000000000000000444,NULL);
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
INSERT INTO region VALUES('regionA',NULL);
INSERT INTO region VALUES('regionB',NULL);
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
CREATE TABLE storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO storage_duration VALUES('regionA','BATT_GRID',2.0,'2 hours energy storage');
INSERT INTO storage_duration VALUES('regionB','BATT_GRID',2.0,'2 hours energy storage');
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
INSERT INTO TimeOfDay VALUES(1,'morning');
INSERT INTO TimeOfDay VALUES(2,'afternoon');
INSERT INTO TimeOfDay VALUES(3,'evening');
INSERT INTO TimeOfDay VALUES(4,'overnight');
CREATE TABLE time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_periodType (label)
);
INSERT INTO time_period VALUES(1,1990,'e');
INSERT INTO time_period VALUES(2,2000,'f');
INSERT INTO time_period VALUES(3,2010,'f');
INSERT INTO time_period VALUES(4,2020,'f');
INSERT INTO time_period VALUES(5,2030,'f');
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
INSERT INTO technology VALUES('IMPORT_LI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'lithium importer');
INSERT INTO technology VALUES('IMPORT_CO','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'cobalt importer');
INSERT INTO technology VALUES('IMPORT_P','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'phosphorous importer');
INSERT INTO technology VALUES('CAR_BEV','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - battery electric');
INSERT INTO technology VALUES('CAR_PHEV','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - plug in hybrid');
INSERT INTO technology VALUES('CAR_ICE','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - internal combustion');
INSERT INTO technology VALUES('RECYCLE_NMC','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'nmc battery recycler');
INSERT INTO technology VALUES('RECYCLE_LFP','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'lfp battery recycler');
INSERT INTO technology VALUES('MANUFAC_NMC','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'nmc battery manufacturing');
INSERT INTO technology VALUES('MANUFAC_LFP','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'lfp battery manufacturing');
INSERT INTO technology VALUES('IMPORT_NI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'nickel importer');
INSERT INTO technology VALUES('DOMESTIC_NI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'domestic nickel production');
INSERT INTO technology VALUES('GEN_DSL','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,'diesel generators');
INSERT INTO technology VALUES('SOL_PV','p','electricity',NULL,NULL,0,0,0,1,0,0,0,0,'solar panels');
INSERT INTO technology VALUES('BATT_GRID','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,0,'grid battery storage');
INSERT INTO technology VALUES('FURNACE','p','residential',NULL,NULL,1,0,0,0,0,0,0,0,'diesel furnace heater');
INSERT INTO technology VALUES('HEATPUMP','p','residential',NULL,NULL,1,0,0,0,0,0,0,0,'heat pump');
INSERT INTO technology VALUES('IMPORT_DSL','p','fuels',NULL,NULL,1,1,0,0,0,0,0,0,'diesel importer');
INSERT INTO technology VALUES('ELEC_INTERTIE','p','electricity',NULL,NULL,0,0,0,0,0,0,1,0,'dummy tech to make landfill feasible');
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
COMMIT;
