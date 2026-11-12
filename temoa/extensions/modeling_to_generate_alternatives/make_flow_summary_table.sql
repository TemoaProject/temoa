BEGIN;

-- The yearly flow tables, as in temoa_schema_v4.sql, for databases made before they were added.
-- Each flow summed over the time slices of its period. Every technology's flows are here; an
-- annual technology's flows are reported only here.

CREATE TABLE IF NOT EXISTS output_flow_in_summary
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES sector_label (sector),
    period      INTEGER
        REFERENCES time_period (period),
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
    PRIMARY KEY (scenario, region, period, input_comm, tech, vintage, output_comm)
);

CREATE TABLE IF NOT EXISTS output_flow_out_summary
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES sector_label (sector),
    period      INTEGER
        REFERENCES time_period (period),
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
    PRIMARY KEY (scenario, region, period, input_comm, tech, vintage, output_comm)
);

COMMIT;
