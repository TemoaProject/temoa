PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS metadata
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
REPLACE INTO metadata
VALUES ('DB_MAJOR', 4, 'DB major version number');
REPLACE INTO metadata
VALUES ('DB_MINOR', 0, 'DB minor version number');
REPLACE INTO metadata
VALUES ('days_per_period', 365, 'count of days in each period');

CREATE TABLE IF NOT EXISTS metadata_real
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
REPLACE INTO metadata_real
VALUES ('global_discount_rate', 0.05, 'Discount Rate for future costs');
REPLACE INTO metadata_real
VALUES ('default_loan_rate', 0.05, 'Default Loan Rate if not specified in LoanRate table');

CREATE TABLE IF NOT EXISTS output_dual_variable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
CREATE TABLE IF NOT EXISTS output_objective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
);
CREATE TABLE IF NOT EXISTS season_label
(
    season TEXT PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE IF NOT EXISTS sector_label
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE IF NOT EXISTS capacity_credit
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
CREATE TABLE IF NOT EXISTS capacity_factor_process
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
CREATE TABLE IF NOT EXISTS capacity_factor_tech
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
CREATE TABLE IF NOT EXISTS capacity_to_activity
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    c2a    REAL,
    units  TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES commodity_type (label),
    description TEXT,
    units       TEXT
);
CREATE TABLE IF NOT EXISTS commodity_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO commodity_type
VALUES ('s', 'source commodity');
REPLACE INTO commodity_type
VALUES ('a', 'annual commodity');
REPLACE INTO commodity_type
VALUES ('p', 'physical commodity');
REPLACE INTO commodity_type
VALUES ('d', 'demand commodity');
REPLACE INTO commodity_type
VALUES ('e', 'emissions commodity');
REPLACE INTO commodity_type
VALUES ('w', 'waste commodity');
REPLACE INTO commodity_type
VALUES ('wa', 'waste annual commodity');
REPLACE INTO commodity_type
VALUES ('wp', 'waste physical commodity');
CREATE TABLE IF NOT EXISTS construction_input
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
CREATE TABLE IF NOT EXISTS cost_emission
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
CREATE TABLE IF NOT EXISTS cost_fixed
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
CREATE TABLE IF NOT EXISTS cost_invest
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
CREATE TABLE IF NOT EXISTS cost_variable
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
CREATE TABLE IF NOT EXISTS demand
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
CREATE TABLE IF NOT EXISTS demand_specific_distribution
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
CREATE TABLE IF NOT EXISTS end_of_life_output
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
CREATE TABLE IF NOT EXISTS efficiency
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
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
CREATE TABLE IF NOT EXISTS efficiency_variable
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
CREATE TABLE IF NOT EXISTS emission_activity
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
CREATE TABLE IF NOT EXISTS emission_embodied
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
CREATE TABLE IF NOT EXISTS emission_end_of_life
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
CREATE TABLE IF NOT EXISTS existing_capacity
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
CREATE TABLE IF NOT EXISTS tech_group
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
CREATE TABLE IF NOT EXISTS loan_lifetime_process
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    lifetime REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE IF NOT EXISTS loan_rate
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
CREATE TABLE IF NOT EXISTS lifetime_process
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    lifetime REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE IF NOT EXISTS lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS operator
(
	operator TEXT PRIMARY KEY,
	notes TEXT
);
REPLACE INTO operator VALUES('e','equal to');
REPLACE INTO operator VALUES('le','less than or equal to');
REPLACE INTO operator VALUES('ge','greater than or equal to');
CREATE TABLE IF NOT EXISTS limit_growth_capacity
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
CREATE TABLE IF NOT EXISTS limit_degrowth_capacity
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
CREATE TABLE IF NOT EXISTS limit_growth_new_capacity
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
CREATE TABLE IF NOT EXISTS limit_degrowth_new_capacity
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
CREATE TABLE IF NOT EXISTS limit_growth_new_capacity_delta
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
CREATE TABLE IF NOT EXISTS limit_degrowth_new_capacity_delta
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
CREATE TABLE IF NOT EXISTS limit_storage_level_fraction
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
CREATE TABLE IF NOT EXISTS limit_activity
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
CREATE TABLE IF NOT EXISTS limit_activity_share
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
CREATE TABLE IF NOT EXISTS limit_annual_capacity_factor
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
CREATE TABLE IF NOT EXISTS limit_capacity
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
CREATE TABLE IF NOT EXISTS limit_capacity_share
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
CREATE TABLE IF NOT EXISTS limit_new_capacity
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
CREATE TABLE IF NOT EXISTS limit_new_capacity_share
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
CREATE TABLE IF NOT EXISTS limit_resource
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
CREATE TABLE IF NOT EXISTS limit_seasonal_capacity_factor
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
CREATE TABLE IF NOT EXISTS limit_tech_input_split
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
CREATE TABLE IF NOT EXISTS limit_tech_input_split_annual
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
CREATE TABLE IF NOT EXISTS limit_tech_output_split
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
CREATE TABLE IF NOT EXISTS limit_tech_output_split_annual
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
CREATE TABLE IF NOT EXISTS limit_emission
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
CREATE TABLE IF NOT EXISTS linked_tech
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
CREATE TABLE IF NOT EXISTS output_curtailment
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
    units       TEXT,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS output_net_capacity
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
    units    TEXT,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS output_built_capacity
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
    units    TEXT,
    PRIMARY KEY (region, scenario, tech, vintage)
);
CREATE TABLE IF NOT EXISTS output_retired_capacity
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
    units     TEXT,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS output_flow_in
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
    units       TEXT,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS output_flow_out
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
    units       TEXT,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE IF NOT EXISTS output_storage_level
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
    units TEXT,
    PRIMARY KEY (scenario, region, period, season, tod, tech, vintage)
);
CREATE TABLE IF NOT EXISTS planning_reserve_margin
(
    region TEXT
        PRIMARY KEY
        REFERENCES region (region),
    margin REAL,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS ramp_down_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS ramp_up_hourly
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    rate   REAL,
    notes TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
CREATE TABLE IF NOT EXISTS reserve_capacity_derate
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
CREATE TABLE IF NOT EXISTS time_segment_fraction
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
CREATE TABLE IF NOT EXISTS storage_duration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS lifetime_survival_curve
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
CREATE TABLE IF NOT EXISTS technology_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO technology_type
VALUES ('p', 'production technology');
REPLACE INTO technology_type
VALUES ('pb', 'baseload production technology');
REPLACE INTO technology_type
VALUES ('ps', 'storage production technology');
-- CREATE TABLE IF NOT EXISTS time_manual
-- (
--     period       INTEGER
--         REFERENCES time_period (period),
--     season TEXT
--        REFERENCES season_label (season),
--     tod          TEXT
--         REFERENCES time_of_day (tod),
--     season_next TEXT
--        REFERENCES season_label (season),
--     tod_next     TEXT
--         REFERENCES time_of_day (tod),
--     notes        TEXT,
--     PRIMARY KEY (period, season, tod)
-- );
CREATE TABLE IF NOT EXISTS time_of_day
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_period_type (label)
);
CREATE TABLE IF NOT EXISTS time_period_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
REPLACE INTO time_period_type
VALUES('e', 'existing vintages');
REPLACE INTO time_period_type
VALUES('f', 'future');
CREATE TABLE IF NOT EXISTS output_emission
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
    units     TEXT,
    PRIMARY KEY (region, scenario, period, emis_comm, tech, vintage)
);
CREATE TABLE IF NOT EXISTS rps_requirement
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
CREATE TABLE IF NOT EXISTS tech_group_member
(
    group_name TEXT
        REFERENCES tech_group (group_name),
    tech       TEXT
        REFERENCES technology (tech),
    PRIMARY KEY (group_name, tech)
);
CREATE TABLE IF NOT EXISTS technology
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
CREATE TABLE IF NOT EXISTS output_cost
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
    units    TEXT,
    PRIMARY KEY (scenario, region, period, tech, vintage),
    FOREIGN KEY (vintage) REFERENCES time_period (period),
    FOREIGN KEY (tech) REFERENCES technology (tech)
);

CREATE TABLE IF NOT EXISTS time_season
(
    period INTEGER REFERENCES time_period (period),
    sequence INTEGER,
    season TEXT REFERENCES season_label(season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);

CREATE TABLE IF NOT EXISTS time_season_sequential
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

CREATE TABLE IF NOT EXISTS myopic_efficiency
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
-- for efficient searching by rtv:
CREATE INDEX IF NOT EXISTS region_tech_vintage ON myopic_efficiency (region, tech, vintage);

CREATE TABLE IF NOT EXISTS output_flow_out_summary
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

COMMIT;
PRAGMA foreign_keys = ON;
