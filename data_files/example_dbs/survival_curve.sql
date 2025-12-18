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
INSERT INTO "commodity" VALUES('source','s',NULL);
INSERT INTO "commodity" VALUES('demand','d',NULL);
CREATE TABLE commodity_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO "commodity_type" VALUES('p','physical commodity');
INSERT INTO "commodity_type" VALUES('a','annual commodity');
INSERT INTO "commodity_type" VALUES('e','emissions commodity');
INSERT INTO "commodity_type" VALUES('d','demand commodity');
INSERT INTO "commodity_type" VALUES('s','source commodity');
INSERT INTO "commodity_type" VALUES('w','waste commodity');
INSERT INTO "commodity_type" VALUES('wa','waste annual commodity');
INSERT INTO "commodity_type" VALUES('wp','waste physical commodity');
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
INSERT INTO "cost_fixed" VALUES('region',2025,'tech_ancient',1994,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2025,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2030,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2035,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2040,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2025,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2030,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2035,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2040,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2045,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2050,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2030,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2035,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2040,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2045,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2050,'tech_future',2050,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2035,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2040,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2045,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2050,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2040,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2045,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2050,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2045,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2050,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_fixed" VALUES('region',2050,'tech_future',2030,1.0,NULL,NULL);
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
INSERT INTO "cost_invest" VALUES('region','tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('region','tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('region','tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('region','tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('region','tech_future',2045,1.0,NULL,NULL);
INSERT INTO "cost_invest" VALUES('region','tech_future',2050,1.0,NULL,NULL);
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
INSERT INTO "cost_variable" VALUES('region',2025,'tech_ancient',1994,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2025,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2030,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2035,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2040,'tech_old',2010,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2025,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2030,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2035,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2040,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2045,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2050,'tech_current',2025,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2030,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2035,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2040,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2045,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2050,'tech_future',2050,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2035,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2040,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2045,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2050,'tech_future',2045,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2040,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2045,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2050,'tech_future',2040,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2045,'tech_future',2030,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2050,'tech_future',2035,1.0,NULL,NULL);
INSERT INTO "cost_variable" VALUES('region',2050,'tech_future',2030,1.0,NULL,NULL);
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
INSERT INTO "demand" VALUES('region',2025,'demand',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('region',2030,'demand',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('region',2035,'demand',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('region',2040,'demand',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('region',2045,'demand',1.0,NULL,NULL);
INSERT INTO "demand" VALUES('region',2050,'demand',1.0,NULL,NULL);
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
INSERT INTO "efficiency" VALUES('region','source','tech_ancient',1994,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_old',2010,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_current',2025,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_future',2030,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_future',2035,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_future',2040,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_future',2045,'demand',1.0,NULL);
INSERT INTO "efficiency" VALUES('region','source','tech_future',2050,'demand',1.0,NULL);
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
INSERT INTO "existing_capacity" VALUES('region','tech_ancient',1994,3.0,NULL,NULL);
INSERT INTO "existing_capacity" VALUES('region','tech_old',2010,0.7,NULL,NULL);
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
INSERT INTO "lifetime_survival_curve" VALUES('region',1994,'tech_ancient',1994,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',1999,'tech_ancient',1994,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2004,'tech_ancient',1994,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2009,'tech_ancient',1994,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2014,'tech_ancient',1994,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2019,'tech_ancient',1994,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2029,'tech_ancient',1994,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2010,'tech_old',2010,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2015,'tech_old',2010,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2020,'tech_old',2010,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2025,'tech_old',2010,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2030,'tech_old',2010,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2035,'tech_old',2010,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2045,'tech_old',2010,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2025,'tech_current',2025,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2030,'tech_current',2025,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2035,'tech_current',2025,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2040,'tech_current',2025,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2045,'tech_current',2025,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2050,'tech_current',2025,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2060,'tech_current',2025,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2030,'tech_future',2030,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2035,'tech_future',2030,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2040,'tech_future',2030,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2045,'tech_future',2030,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2050,'tech_future',2030,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2055,'tech_future',2030,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2065,'tech_future',2030,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2035,'tech_future',2035,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2040,'tech_future',2035,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2045,'tech_future',2035,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2050,'tech_future',2035,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2055,'tech_future',2035,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2060,'tech_future',2035,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2070,'tech_future',2035,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2040,'tech_future',2040,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2045,'tech_future',2040,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2050,'tech_future',2040,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2055,'tech_future',2040,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2060,'tech_future',2040,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2065,'tech_future',2040,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2075,'tech_future',2040,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2045,'tech_future',2045,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2050,'tech_future',2045,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2055,'tech_future',2045,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2060,'tech_future',2045,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2065,'tech_future',2045,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2070,'tech_future',2045,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2080,'tech_future',2045,0.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2050,'tech_future',2050,1.0,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2055,'tech_future',2050,0.97,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2060,'tech_future',2050,8.80000000000000115e-01,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2065,'tech_future',2050,0.62,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2070,'tech_future',2050,0.27,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2075,'tech_future',2050,0.08,NULL);
INSERT INTO "lifetime_survival_curve" VALUES('region',2085,'tech_future',2050,0.0,NULL);
CREATE TABLE lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "lifetime_tech" VALUES('region','tech_ancient',35.0,NULL);
INSERT INTO "lifetime_tech" VALUES('region','tech_old',35.0,NULL);
INSERT INTO "lifetime_tech" VALUES('region','tech_current',35.0,NULL);
INSERT INTO "lifetime_tech" VALUES('region','tech_future',35.0,NULL);
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
INSERT INTO "region" VALUES('region',NULL);
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
INSERT INTO "season_label" VALUES('s',NULL);
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
INSERT INTO "technology" VALUES('tech_ancient','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO "technology" VALUES('tech_old','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO "technology" VALUES('tech_current','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO "technology" VALUES('tech_future','p','energy',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
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
INSERT INTO "time_of_day" VALUES(0,'d');
CREATE TABLE time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_period_type (label)
);
INSERT INTO "time_period" VALUES(-2,1994,'e');
INSERT INTO "time_period" VALUES(-1,2010,'e');
INSERT INTO "time_period" VALUES(0,2025,'f');
INSERT INTO "time_period" VALUES(1,2030,'f');
INSERT INTO "time_period" VALUES(2,2035,'f');
INSERT INTO "time_period" VALUES(3,2040,'f');
INSERT INTO "time_period" VALUES(4,2045,'f');
INSERT INTO "time_period" VALUES(5,2050,'f');
INSERT INTO "time_period" VALUES(6,2055,'f');
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
INSERT INTO "time_season" VALUES(2025,0,'s',NULL);
INSERT INTO "time_season" VALUES(2030,1,'s',NULL);
INSERT INTO "time_season" VALUES(2035,2,'s',NULL);
INSERT INTO "time_season" VALUES(2040,3,'s',NULL);
INSERT INTO "time_season" VALUES(2045,4,'s',NULL);
INSERT INTO "time_season" VALUES(2050,5,'s',NULL);

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
INSERT INTO "time_segment_fraction" VALUES(2025,'s','d',1.0,NULL);
INSERT INTO "time_segment_fraction" VALUES(2030,'s','d',1.0,NULL);
INSERT INTO "time_segment_fraction" VALUES(2035,'s','d',1.0,NULL);
INSERT INTO "time_segment_fraction" VALUES(2040,'s','d',1.0,NULL);
INSERT INTO "time_segment_fraction" VALUES(2045,'s','d',1.0,NULL);
INSERT INTO "time_segment_fraction" VALUES(2050,'s','d',1.0,NULL);
CREATE INDEX region_tech_vintage ON myopic_efficiency (region, tech, vintage);
COMMIT;
