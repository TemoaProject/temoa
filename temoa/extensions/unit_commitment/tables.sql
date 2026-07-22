CREATE TABLE IF NOT EXISTS unit_commitment
(
    region               TEXT    NOT NULL,
    tech                 TEXT    NOT NULL,
    unit_capacity        REAL    NOT NULL,
    min_output_fraction  REAL    NOT NULL DEFAULT 0.0,
    max_output_fraction  REAL    NOT NULL DEFAULT 1.0,
    min_up_time_hours    INTEGER NOT NULL DEFAULT 0,
    min_down_time_hours  INTEGER NOT NULL DEFAULT 0,
    linearized           INTEGER NOT NULL DEFAULT 0,
    units                TEXT,
    notes                TEXT,
    CHECK (unit_capacity > 0),
    CHECK (0 <= min_output_fraction AND min_output_fraction <= 1),
    CHECK (0 < max_output_fraction AND max_output_fraction <= 1),
    CHECK (min_up_time_hours >= 0),
    CHECK (min_down_time_hours >= 0),
    CHECK (linearized IN (0, 1)),
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS unit_commitment_startup_cost
(
    region                          TEXT NOT NULL,
    tech                            TEXT NOT NULL,
    cost_per_cap                    REAL NOT NULL DEFAULT 0.0,
    units                           TEXT,
    notes                           TEXT,
    CHECK (cost_per_cap > 0),
    PRIMARY KEY (region, tech)
);
CREATE TABLE IF NOT EXISTS unit_commitment_startup_emissions
(
    region                          TEXT NOT NULL,
    emis_comm                       TEXT NOT NULL DEFAULT '',
    tech                            TEXT NOT NULL,
    emis_per_cap                    REAL NOT NULL DEFAULT 0.0,
    units                           TEXT,
    notes                           TEXT,
    CHECK (emis_per_cap > 0),
    PRIMARY KEY (region, emis_comm, tech)
);
CREATE TABLE IF NOT EXISTS unit_commitment_startup_input
(
    region                          TEXT NOT NULL,
    input_comm                      TEXT NOT NULL DEFAULT '',
    tech                            TEXT NOT NULL,
    input_per_cap                   REAL NOT NULL DEFAULT 0.0,
    units                           TEXT,
    notes                           TEXT,
    CHECK (input_per_cap > 0),
    PRIMARY KEY (region, input_comm, tech)
);
CREATE TABLE IF NOT EXISTS output_unit_commitment
(
    scenario                        TEXT NOT NULL,
    region                          TEXT NOT NULL,
    sector                          TEXT NOT NULL,
    period                          INTEGER NOT NULL,
    season                          TEXT NOT NULL,
    tod                             TEXT NOT NULL,
    tech                            TEXT NOT NULL,
    vintage                         INTEGER NOT NULL,
    online_cap                      REAL,
    start_cap                       REAL,
    stop_cap                        REAL,
    units                           TEXT,
    PRIMARY KEY (scenario, region, sector, period, season, tod, tech, vintage)
);
