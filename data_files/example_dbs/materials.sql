BEGIN TRANSACTION;
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
        REFERENCES season_label (season),
    tod     TEXT
        REFERENCES time_of_day (tod),
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
        REFERENCES season_label (season),
    tod    TEXT
        REFERENCES time_of_day (tod),
    tech   TEXT
        REFERENCES technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, period, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'summer','morning','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'autumn','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'winter','morning','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'spring','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'summer','afternoon','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'autumn','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'winter','afternoon','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'spring','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'summer','evening','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2000,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'summer','morning','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'autumn','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'winter','morning','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'spring','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'summer','afternoon','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'autumn','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'winter','afternoon','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'spring','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'summer','evening','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2010,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'summer','morning','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'autumn','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'winter','morning','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'spring','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'summer','afternoon','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'autumn','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'winter','afternoon','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'spring','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'summer','evening','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionA',2020,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'summer','morning','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'autumn','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'winter','morning','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'spring','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'summer','afternoon','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'autumn','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'winter','afternoon','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'spring','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'summer','evening','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2000,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'summer','morning','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'autumn','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'winter','morning','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'spring','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'summer','afternoon','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'autumn','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'winter','afternoon','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'spring','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'summer','evening','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2010,'spring','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'summer','morning','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'autumn','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'winter','morning','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'spring','morning','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'summer','afternoon','SOL_PV',0.3,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'autumn','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'winter','afternoon','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'spring','afternoon','SOL_PV',0.2,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'summer','evening','SOL_PV',0.1,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'autumn','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'winter','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'spring','evening','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'summer','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'autumn','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'winter','overnight','SOL_PV',0.0,NULL);
INSERT INTO "capacity_factor_tech" VALUES('RegionB',2020,'spring','overnight','SOL_PV',0.0,NULL);
CREATE TABLE capacity_to_activity
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
        REFERENCES commodity_type (label),
    description TEXT
);
INSERT INTO "commodity" VALUES('ethos','s','import dummy source');
INSERT INTO "commodity" VALUES('electricity','p','grid electricity');
INSERT INTO "commodity" VALUES('passenger_km','d','demand for passenger km');
INSERT INTO "commodity" VALUES('battery_nmc','a','battery - lithium nickel manganese cobalt oxide');
INSERT INTO "commodity" VALUES('battery_lfp','a','battery - lithium iron phosphate');
INSERT INTO "commodity" VALUES('lithium','a','lithium');
INSERT INTO "commodity" VALUES('cobalt','a','cobalt');
INSERT INTO "commodity" VALUES('phosphorous','a','phosphorous');
INSERT INTO "commodity" VALUES('diesel','a','diesel');
INSERT INTO "commodity" VALUES('heating','d','demand for residential heating');
INSERT INTO "commodity" VALUES('nickel','a','nickel');
INSERT INTO "commodity" VALUES('used_batt_nmc','wa','used battery - lithium nickel manganese cobalt oxide');
INSERT INTO "commodity" VALUES('used_batt_lfp','wa','used battery - lithium iron phosphate');
INSERT INTO "commodity" VALUES('co2e','e','emitted co2-equivalent GHGs');
INSERT INTO "commodity" VALUES('waste_steel','w','waste steel from cars');
CREATE TABLE commodity_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO "commodity_type" VALUES('w','waste commodity');
INSERT INTO "commodity_type" VALUES('wa','waste annual commodity');
INSERT INTO "commodity_type" VALUES('wp','waste physical commodity');
INSERT INTO "commodity_type" VALUES('a','annual commodity');
INSERT INTO "commodity_type" VALUES('p','physical commodity');
INSERT INTO "commodity_type" VALUES('e','emissions commodity');
INSERT INTO "commodity_type" VALUES('d','demand commodity');
INSERT INTO "commodity_type" VALUES('s','source commodity');
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
INSERT INTO "construction_input" VALUES('RegionA','battery_nmc','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionA','battery_lfp','CAR_PHEV',2000,0.1,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionA','battery_nmc','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionA','battery_lfp','CAR_PHEV',2010,0.1,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionA','battery_nmc','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionA','battery_lfp','CAR_PHEV',2020,0.1,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionB','battery_nmc','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionB','battery_lfp','CAR_PHEV',2000,0.1,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionB','battery_nmc','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionB','battery_lfp','CAR_PHEV',2010,0.1,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionB','battery_nmc','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO "construction_input" VALUES('RegionB','battery_lfp','CAR_PHEV',2020,0.1,NULL,NULL);
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
INSERT INTO "cost_emission" VALUES('RegionA',2000,'co2e',1.0,NULL,NULL);
INSERT INTO "cost_emission" VALUES('RegionA',2010,'co2e',1.0,NULL,NULL);
INSERT INTO "cost_emission" VALUES('RegionA',2020,'co2e',1.0,NULL,NULL);
INSERT INTO "cost_emission" VALUES('RegionB',2000,'co2e',1.0,NULL,NULL);
INSERT INTO "cost_emission" VALUES('RegionB',2010,'co2e',1.0,NULL,NULL);
INSERT INTO "cost_emission" VALUES('RegionB',2020,'co2e',1.0,NULL,NULL);
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
INSERT INTO "cost_invest" VALUES('RegionA','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_PHEV',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_PHEV',2010,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_PHEV',2020,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_ICE',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_ICE',2010,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','CAR_ICE',2020,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','RECYCLE_NMC',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','RECYCLE_LFP',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','MANUFAC_NMC',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','MANUFAC_LFP',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','BATT_GRID',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','SOL_PV',2000,10.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA','GEN_DSL',2000,2.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_BEV',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_BEV',2010,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_BEV',2020,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_PHEV',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_PHEV',2010,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_PHEV',2020,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_ICE',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_ICE',2010,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','CAR_ICE',2020,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','RECYCLE_NMC',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','RECYCLE_LFP',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','MANUFAC_NMC',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','MANUFAC_LFP',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','BATT_GRID',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','GEN_DSL',2000,2.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionA-RegionB','ELEC_INTERTIE',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB-RegionA','ELEC_INTERTIE',2000,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('RegionB','SOL_PV',2000,1.0,NULL,NULL);
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
INSERT INTO "cost_variable" VALUES('RegionA',2000,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2010,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2020,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2000,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2010,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2020,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2000,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2010,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2020,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2000,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2010,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2020,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2000,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2010,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2020,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2000,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2010,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionA',2020,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2000,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2010,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2020,'IMPORT_DSL',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2000,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2010,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2020,'IMPORT_LI',2000,2.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2000,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2010,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2020,'IMPORT_NI',2000,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2000,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2010,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2020,'IMPORT_CO',2000,5.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2000,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2010,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2020,'IMPORT_P',2000,3.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2000,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2010,'DOMESTIC_NI',2000,0.5,NULL,NULL);
INSERT INTO "cost_variable" VALUES('RegionB',2020,'DOMESTIC_NI',2000,0.5,NULL,NULL);
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
INSERT INTO "demand" VALUES('RegionA',2000,'passenger_km',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionA',2010,'passenger_km',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionA',2020,'passenger_km',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionA',2000,'heating',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionA',2010,'heating',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionA',2020,'heating',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionB',2000,'passenger_km',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionB',2010,'passenger_km',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionB',2020,'passenger_km',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionB',2000,'heating',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionB',2010,'heating',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('RegionB',2020,'heating',1.0,NULL,NULL);
CREATE TABLE demand_specific_distribution
(
    region      TEXT,
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod         TEXT
        REFERENCES time_of_day (tod),
    demand_name TEXT
        REFERENCES commodity (name),
    dsd         REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'summer','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'autumn','morning','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'winter','morning','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'spring','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'summer','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'autumn','afternoon','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'winter','afternoon','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'spring','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'summer','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'autumn','evening','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'winter','evening','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'spring','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'summer','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'autumn','overnight','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'winter','overnight','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2000,'spring','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'summer','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'autumn','morning','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'winter','morning','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'spring','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'summer','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'autumn','afternoon','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'winter','afternoon','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'spring','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'summer','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'autumn','evening','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'winter','evening','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'spring','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'summer','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'autumn','overnight','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'winter','overnight','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2010,'spring','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'summer','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'autumn','morning','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'winter','morning','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'spring','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'summer','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'autumn','afternoon','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'winter','afternoon','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'spring','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'summer','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'autumn','evening','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'winter','evening','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'spring','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'summer','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'autumn','overnight','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'winter','overnight','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionA',2020,'spring','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'summer','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'autumn','morning','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'winter','morning','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'spring','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'summer','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'autumn','afternoon','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'winter','afternoon','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'spring','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'summer','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'autumn','evening','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'winter','evening','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'spring','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'summer','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'autumn','overnight','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'winter','overnight','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2000,'spring','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'summer','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'autumn','morning','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'winter','morning','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'spring','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'summer','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'autumn','afternoon','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'winter','afternoon','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'spring','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'summer','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'autumn','evening','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'winter','evening','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'spring','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'summer','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'autumn','overnight','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'winter','overnight','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2010,'spring','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'summer','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'autumn','morning','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'winter','morning','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'spring','morning','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'summer','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'autumn','afternoon','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'winter','afternoon','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'spring','afternoon','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'summer','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'autumn','evening','heating',0.08,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'winter','evening','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'spring','evening','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'summer','overnight','heating',0.0,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'autumn','overnight','heating',0.12,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'winter','overnight','heating',0.16,NULL);
INSERT INTO "demand_specific_distribution" VALUES('RegionB',2020,'spring','overnight','heating',0.0,NULL);
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
INSERT INTO "efficiency" VALUES('RegionA','ethos','DOMESTIC_NI',2000,'nickel',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','ethos','IMPORT_LI',2000,'lithium',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','ethos','IMPORT_NI',2000,'nickel',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','ethos','IMPORT_CO',2000,'cobalt',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','ethos','IMPORT_P',2000,'phosphorous',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','used_batt_nmc','RECYCLE_NMC',2000,'battery_nmc',0.2,NULL);
INSERT INTO "efficiency" VALUES('RegionA','used_batt_lfp','RECYCLE_LFP',2000,'battery_lfp',0.2,NULL);
INSERT INTO "efficiency" VALUES('RegionA','lithium','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','nickel','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','cobalt','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','lithium','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','phosphorous','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','RECYCLE_NMC',2000,'battery_nmc',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionA','electricity','RECYCLE_LFP',2000,'battery_lfp',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionA','electricity','MANUFAC_NMC',2000,'battery_nmc',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionA','electricity','MANUFAC_LFP',2000,'battery_lfp',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionA','diesel','GEN_DSL',2000,'electricity',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','ethos','SOL_PV',2000,'electricity',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','BATT_GRID',2000,'electricity',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','FURNACE',2000,'heating',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','HEATPUMP',2000,'heating',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_BEV',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_ICE',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_BEV',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_ICE',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_BEV',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_ICE',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_BEV',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','electricity','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA','diesel','CAR_ICE',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','DOMESTIC_NI',2000,'nickel',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','IMPORT_LI',2000,'lithium',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','IMPORT_NI',2000,'nickel',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','IMPORT_CO',2000,'cobalt',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','IMPORT_P',2000,'phosphorous',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','used_batt_nmc','RECYCLE_NMC',2000,'battery_nmc',0.2,NULL);
INSERT INTO "efficiency" VALUES('RegionB','used_batt_lfp','RECYCLE_LFP',2000,'battery_lfp',0.2,NULL);
INSERT INTO "efficiency" VALUES('RegionB','lithium','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','nickel','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','cobalt','MANUFAC_NMC',2000,'battery_nmc',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','lithium','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','phosphorous','MANUFAC_LFP',2000,'battery_lfp',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','RECYCLE_NMC',2000,'battery_nmc',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionB','electricity','RECYCLE_LFP',2000,'battery_lfp',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionB','electricity','MANUFAC_NMC',2000,'battery_nmc',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionB','electricity','MANUFAC_LFP',2000,'battery_lfp',0.001,'Effectively zero');
INSERT INTO "efficiency" VALUES('RegionB','diesel','GEN_DSL',2000,'electricity',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','SOL_PV',2000,'electricity',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','BATT_GRID',2000,'electricity',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','FURNACE',2000,'heating',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','HEATPUMP',2000,'heating',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_BEV',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_PHEV',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_ICE',1990,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_BEV',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_PHEV',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_ICE',2000,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_BEV',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_PHEV',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_ICE',2010,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_BEV',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','electricity','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_PHEV',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionB','diesel','CAR_ICE',2020,'passenger_km',1.0,NULL);
INSERT INTO "efficiency" VALUES('RegionA-RegionB','electricity','ELEC_INTERTIE',2000,'electricity',0.9,NULL);
INSERT INTO "efficiency" VALUES('RegionB-RegionA','electricity','ELEC_INTERTIE',2000,'electricity',0.9,NULL);
CREATE TABLE efficiency_variable
(
    region      TEXT,
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod         TEXT
        REFERENCES time_of_day (tod),
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
INSERT INTO "emission_activity" VALUES('RegionA','co2e','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL,'assumed combusted');
INSERT INTO "emission_activity" VALUES('RegionB','co2e','ethos','IMPORT_DSL',2000,'diesel',1.0,NULL,'assumed combusted');
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
    PRIMARY KEY (region, emis_comm, tech, vintage)
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
    PRIMARY KEY (region, emis_comm, tech, vintage)
);
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
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_BEV',1990,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_PHEV',1990,'used_batt_lfp',0.1,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_BEV',2000,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_PHEV',2000,'used_batt_lfp',0.1,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_BEV',2010,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_PHEV',2010,'used_batt_lfp',0.1,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_BEV',1990,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_PHEV',1990,'used_batt_lfp',0.1,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_BEV',2000,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_PHEV',2000,'used_batt_lfp',0.1,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_BEV',2010,'used_batt_nmc',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_PHEV',2010,'used_batt_lfp',0.1,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_BEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_ICE',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_PHEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_BEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_ICE',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_PHEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_BEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_ICE',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionA','CAR_PHEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_BEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_ICE',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_PHEV',1990,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_BEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_ICE',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_PHEV',2000,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_BEV',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_ICE',2010,'waste_steel',1.0,NULL,NULL);
INSERT INTO "end_of_life_output" VALUES('RegionB','CAR_PHEV',2010,'waste_steel',1.0,NULL,NULL);
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
INSERT INTO "existing_capacity" VALUES('RegionA','CAR_BEV',1990,1.0,NULL,NULL);
INSERT INTO "existing_capacity" VALUES('RegionA','CAR_PHEV',1990,1.0,NULL,NULL);
INSERT INTO "existing_capacity" VALUES('RegionA','CAR_ICE',1990,1.0,NULL,NULL);
INSERT INTO "existing_capacity" VALUES('RegionB','CAR_BEV',1990,1.0,NULL,NULL);
INSERT INTO "existing_capacity" VALUES('RegionB','CAR_PHEV',1990,1.0,NULL,NULL);
INSERT INTO "existing_capacity" VALUES('RegionB','CAR_ICE',1990,1.0,NULL,NULL);
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
CREATE TABLE lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "lifetime_tech" VALUES('RegionA','CAR_BEV',10.0,NULL);
INSERT INTO "lifetime_tech" VALUES('RegionA','CAR_PHEV',10.0,NULL);
INSERT INTO "lifetime_tech" VALUES('RegionA','CAR_ICE',10.0,NULL);
INSERT INTO "lifetime_tech" VALUES('RegionB','CAR_BEV',10.0,NULL);
INSERT INTO "lifetime_tech" VALUES('RegionB','CAR_PHEV',10.0,NULL);
INSERT INTO "lifetime_tech" VALUES('RegionB','CAR_ICE',10.0,NULL);
CREATE TABLE limit_activity
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE limit_degrowth_capacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_emission
(
    region    TEXT,
    period    INTEGER
        REFERENCES time_period (period),
    emis_comm TEXT
        REFERENCES commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
    value     REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm, operator)
);
CREATE TABLE limit_growth_capacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE limit_new_capacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE limit_resource
(
    region  TEXT,
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
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
        REFERENCES season_label (season),
	tech    TEXT
        REFERENCES technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
	factor	REAL,
	notes	TEXT,
	PRIMARY KEY(region, period, season, tech, operator)
);
CREATE TABLE limit_storage_level_fraction
(
    region   TEXT,
    period   INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod      TEXT
        REFERENCES time_of_day (tod),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES operator (operator),
    fraction REAL,
    notes    TEXT,
    PRIMARY KEY(region, period, season, tod, tech, vintage, operator)
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'lithium','MANUFAC_NMC','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'nickel','MANUFAC_NMC','le',0.15,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'cobalt','MANUFAC_NMC','le',0.04,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'electricity','MANUFAC_NMC','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'lithium','MANUFAC_LFP','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'phosphorous','MANUFAC_LFP','le',0.19,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'electricity','MANUFAC_LFP','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'lithium','MANUFAC_NMC','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'nickel','MANUFAC_NMC','le',0.15,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'cobalt','MANUFAC_NMC','le',0.04,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'electricity','MANUFAC_NMC','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'lithium','MANUFAC_LFP','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'phosphorous','MANUFAC_LFP','le',0.19,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'electricity','MANUFAC_LFP','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'lithium','MANUFAC_NMC','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'nickel','MANUFAC_NMC','le',0.15,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'cobalt','MANUFAC_NMC','le',0.04,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'electricity','MANUFAC_NMC','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'lithium','MANUFAC_LFP','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'phosphorous','MANUFAC_LFP','le',0.19,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'electricity','MANUFAC_LFP','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'electricity','CAR_PHEV','le',0.2,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2000,'diesel','CAR_PHEV','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'electricity','CAR_PHEV','le',0.2,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2010,'diesel','CAR_PHEV','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'electricity','CAR_PHEV','le',0.2,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionA',2020,'diesel','CAR_PHEV','le',0.8,NULL);
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'lithium','MANUFAC_NMC','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'nickel','MANUFAC_NMC','le',0.15,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'cobalt','MANUFAC_NMC','le',0.04,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'electricity','MANUFAC_NMC','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'lithium','MANUFAC_LFP','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'phosphorous','MANUFAC_LFP','le',0.19,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'electricity','MANUFAC_LFP','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'lithium','MANUFAC_NMC','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'nickel','MANUFAC_NMC','le',0.15,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'cobalt','MANUFAC_NMC','le',0.04,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'electricity','MANUFAC_NMC','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'lithium','MANUFAC_LFP','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'phosphorous','MANUFAC_LFP','le',0.19,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'electricity','MANUFAC_LFP','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'lithium','MANUFAC_NMC','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'nickel','MANUFAC_NMC','le',0.15,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'cobalt','MANUFAC_NMC','le',0.04,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'electricity','MANUFAC_NMC','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'lithium','MANUFAC_LFP','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'phosphorous','MANUFAC_LFP','le',0.19,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'electricity','MANUFAC_LFP','le',0.01,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'electricity','CAR_PHEV','le',0.2,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2000,'diesel','CAR_PHEV','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'electricity','CAR_PHEV','le',0.2,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2010,'diesel','CAR_PHEV','le',0.8,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'electricity','CAR_PHEV','le',0.2,'');
INSERT INTO "limit_tech_input_split_annual" VALUES('RegionB',2020,'diesel','CAR_PHEV','le',0.8,NULL);
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
    	REFERENCES operator (operator),
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
    	REFERENCES operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
CREATE TABLE linked_tech
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
CREATE TABLE metadata
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
INSERT INTO "metadata" VALUES('days_per_period',365,'count of days in each period');
INSERT INTO "metadata" VALUES('DB_MAJOR',4,'');
INSERT INTO "metadata" VALUES('DB_MINOR',0,'');
CREATE TABLE metadata_real
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO "metadata_real" VALUES('global_discount_rate',0.05,'Discount Rate for future costs');
INSERT INTO "metadata_real" VALUES('default_loan_rate',0.05,'Default Loan Rate if not specified in loan_rate table');
CREATE TABLE myopic_efficiency
(
    base_year   integer,
    region      text,
    input_comm  text,
    tech        text,
    vintage     integer,
    output_comm text,
    efficiency  real,
    lifetime    integer,

    FOREIGN KEY (tech) REFERENCES technology (tech),
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm)
);
CREATE TABLE operator
(
	operator TEXT PRIMARY KEY,
	notes TEXT
);
INSERT INTO "operator" VALUES('e','equal to');
INSERT INTO "operator" VALUES('le','less than or equal to');
INSERT INTO "operator" VALUES('ge','greater than or equal to');
CREATE TABLE output_built_capacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES sector_label (sector),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, tech, vintage)
);
CREATE TABLE output_cost
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT REFERENCES sector_label (sector),
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
        REFERENCES time_of_day (tod),
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
CREATE TABLE output_dual_variable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
CREATE TABLE output_emission
(
    scenario  TEXT,
    region    TEXT,
    sector    TEXT
        REFERENCES sector_label (sector),
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
CREATE TABLE output_flow_in
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES sector_label (sector),
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod         TEXT
        REFERENCES time_of_day (tod),
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
CREATE TABLE output_flow_out
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES sector_label (sector),
    period      INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod         TEXT
        REFERENCES time_of_day (tod),
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
CREATE TABLE output_flow_out_summary
(
    scenario    TEXT NOT NULL,
    region      TEXT NOT NULL,
    sector      TEXT,
    period      INTEGER,
    input_comm  TEXT NOT NULL,
    tech        TEXT NOT NULL,
    vintage     INTEGER,
    output_comm TEXT NOT NULL,
    flow        REAL NOT NULL,

    FOREIGN KEY (tech) REFERENCES technology (tech),
    PRIMARY KEY (scenario, region, period, input_comm, tech, vintage, output_comm)
);
CREATE TABLE output_net_capacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES sector_label (sector),
    period   INTEGER
        REFERENCES time_period (period),
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE output_objective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
);
CREATE TABLE output_retired_capacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES sector_label (sector),
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
CREATE TABLE output_storage_level
(
    scenario TEXT,
    region TEXT,
    sector TEXT
        REFERENCES sector_label (sector),
    period INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod TEXT
        REFERENCES time_of_day (tod),
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
INSERT INTO "region" VALUES('RegionA',NULL);
INSERT INTO "region" VALUES('RegionB',NULL);
CREATE TABLE reserve_capacity_derate
(
    region  TEXT,
    period  INTEGER
        REFERENCES time_period (period),
    season  TEXT
    	REFERENCES season_label (season),
    tech    TEXT
        REFERENCES technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, season, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE rps_requirement
(
    region      TEXT    NOT NULL
        REFERENCES region (region),
    period      INTEGER NOT NULL
        REFERENCES time_period (period),
    tech_group  TEXT    NOT NULL
        REFERENCES tech_group (group_name),
    requirement REAL    NOT NULL,
    notes       TEXT
);
CREATE TABLE season_label
(
    season TEXT PRIMARY KEY,
    notes  TEXT
);
INSERT INTO "season_label" VALUES('summer',NULL);
INSERT INTO "season_label" VALUES('autumn',NULL);
INSERT INTO "season_label" VALUES('winter',NULL);
INSERT INTO "season_label" VALUES('spring',NULL);
CREATE TABLE sector_label
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "storage_duration" VALUES('RegionA','BATT_GRID',2.0,'2 hours energy storage');
INSERT INTO "storage_duration" VALUES('RegionB','BATT_GRID',2.0,'2 hours energy storage');
CREATE TABLE tech_group
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
CREATE TABLE tech_group_member
(
    group_name TEXT
        REFERENCES tech_group (group_name),
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
    FOREIGN KEY (flag) REFERENCES technology_type (label)
);
INSERT INTO "technology" VALUES('IMPORT_LI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'lithium importer');
INSERT INTO "technology" VALUES('IMPORT_CO','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'cobalt importer');
INSERT INTO "technology" VALUES('IMPORT_P','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'phosphorous importer');
INSERT INTO "technology" VALUES('CAR_BEV','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - battery electric');
INSERT INTO "technology" VALUES('CAR_PHEV','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - plug in hybrid');
INSERT INTO "technology" VALUES('CAR_ICE','p','transportation',NULL,NULL,0,0,0,0,0,0,0,0,'car - internal combustion');
INSERT INTO "technology" VALUES('RECYCLE_NMC','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'nmc battery recycler');
INSERT INTO "technology" VALUES('RECYCLE_LFP','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'lfp battery recycler');
INSERT INTO "technology" VALUES('MANUFAC_NMC','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'nmc battery manufacturing');
INSERT INTO "technology" VALUES('MANUFAC_LFP','p','materials',NULL,NULL,0,1,0,0,0,0,0,0,'lfp battery manufacturing');
INSERT INTO "technology" VALUES('IMPORT_NI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'nickel importer');
INSERT INTO "technology" VALUES('DOMESTIC_NI','p','materials',NULL,NULL,1,1,0,0,0,0,0,0,'domestic nickel production');
INSERT INTO "technology" VALUES('GEN_DSL','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,'diesel generators');
INSERT INTO "technology" VALUES('SOL_PV','p','electricity',NULL,NULL,0,0,0,1,0,0,0,0,'solar panels');
INSERT INTO "technology" VALUES('BATT_GRID','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,0,'grid battery storage');
INSERT INTO "technology" VALUES('FURNACE','p','residential',NULL,NULL,1,0,0,0,0,0,0,0,'diesel furnace heater');
INSERT INTO "technology" VALUES('HEATPUMP','p','residential',NULL,NULL,1,0,0,0,0,0,0,0,'heat pump');
INSERT INTO "technology" VALUES('IMPORT_DSL','p','fuels',NULL,NULL,1,1,0,0,0,0,0,0,'diesel importer');
INSERT INTO "technology" VALUES('ELEC_INTERTIE','p','electricity',NULL,NULL,0,0,0,0,0,0,1,0,'dummy tech to make landfill feasible');
CREATE TABLE technology_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO "technology_type" VALUES('p','production technology');
INSERT INTO "technology_type" VALUES('pb','baseload production technology');
INSERT INTO "technology_type" VALUES('ps','storage production technology');
CREATE TABLE time_of_day
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO "time_of_day" VALUES(1,'morning');
INSERT INTO "time_of_day" VALUES(2,'afternoon');
INSERT INTO "time_of_day" VALUES(3,'evening');
INSERT INTO "time_of_day" VALUES(4,'overnight');
CREATE TABLE time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_period_type (label)
);
INSERT INTO "time_period" VALUES(1,1990,'e');
INSERT INTO "time_period" VALUES(2,2000,'f');
INSERT INTO "time_period" VALUES(3,2010,'f');
INSERT INTO "time_period" VALUES(4,2020,'f');
INSERT INTO "time_period" VALUES(5,2030,'f');
CREATE TABLE time_period_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO "time_period_type" VALUES('e','existing vintages');
INSERT INTO "time_period_type" VALUES('f','future');
CREATE TABLE time_season
(
    period INTEGER REFERENCES time_period (period),
    sequence INTEGER,
    season TEXT REFERENCES season_label(season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
INSERT INTO "time_season" VALUES(2000,1,'summer',NULL);
INSERT INTO "time_season" VALUES(2000,2,'autumn',NULL);
INSERT INTO "time_season" VALUES(2000,3,'winter',NULL);
INSERT INTO "time_season" VALUES(2000,4,'spring',NULL);
INSERT INTO "time_season" VALUES(2010,5,'summer',NULL);
INSERT INTO "time_season" VALUES(2010,6,'autumn',NULL);
INSERT INTO "time_season" VALUES(2010,7,'winter',NULL);
INSERT INTO "time_season" VALUES(2010,8,'spring',NULL);
INSERT INTO "time_season" VALUES(2020,9,'summer',NULL);
INSERT INTO "time_season" VALUES(2020,10,'autumn',NULL);
INSERT INTO "time_season" VALUES(2020,11,'winter',NULL);
INSERT INTO "time_season" VALUES(2020,12,'spring',NULL);

CREATE TABLE time_season_sequential
(
    period INTEGER REFERENCES time_period (period),
    sequence INTEGER,
    seas_seq TEXT,
    season TEXT REFERENCES season_label(season),
    num_days REAL NOT NULL,
    notes TEXT,
    PRIMARY KEY (period, sequence, seas_seq, season),
    CHECK (num_days > 0)
);

CREATE TABLE time_segment_fraction
(
    period INTEGER
        REFERENCES time_period (period),
    season TEXT
        REFERENCES season_label (season),
    tod     TEXT
        REFERENCES time_of_day (tod),
    segment_fraction REAL,
    notes   TEXT,
    PRIMARY KEY (period, season, tod),
    CHECK (segment_fraction >= 0 AND segment_fraction <= 1)
);
INSERT INTO "time_segment_fraction" VALUES(2000,'summer','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'autumn','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'winter','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'spring','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'summer','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'autumn','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'winter','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'spring','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'summer','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'autumn','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'winter','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'spring','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'summer','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'autumn','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'winter','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2000,'spring','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'summer','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'autumn','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'winter','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'spring','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'summer','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'autumn','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'winter','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'spring','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'summer','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'autumn','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'winter','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'spring','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'summer','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'autumn','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'winter','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2010,'spring','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'summer','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'autumn','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'winter','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'spring','morning',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'summer','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'autumn','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'winter','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'spring','afternoon',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'summer','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'autumn','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'winter','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'spring','evening',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'summer','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'autumn','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'winter','overnight',0.0625,NULL);
INSERT INTO "time_segment_fraction" VALUES(2020,'spring','overnight',0.0625,NULL);
CREATE INDEX region_tech_vintage ON myopic_efficiency (region, tech, vintage);
COMMIT;
