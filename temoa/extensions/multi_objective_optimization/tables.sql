CREATE TABLE IF NOT EXISTS moo_activity_weight
(
    objective TEXT,
    region    TEXT,
    period    INTEGER
        REFERENCES time_period (period),
    tech      TEXT
        REFERENCES technology (tech),
    vintage   INTEGER
        REFERENCES time_period (period),
    weight    REAL,
    notes     TEXT,
    PRIMARY KEY (objective, region, period, tech, vintage)
);
CREATE TABLE IF NOT EXISTS moo_built_capacity_weight
(
    objective TEXT,
    region    TEXT,
    tech      TEXT
        REFERENCES technology (tech),
    vintage   INTEGER
        REFERENCES time_period (period),
    weight    REAL,
    notes     TEXT,
    PRIMARY KEY (objective, region, tech, vintage)
);
CREATE TABLE IF NOT EXISTS moo_net_capacity_weight
(
    objective TEXT,
    region    TEXT,
    period    INTEGER
        REFERENCES time_period (period),
    tech      TEXT
        REFERENCES technology (tech),
    vintage   INTEGER
        REFERENCES time_period (period),
    weight    REAL,
    notes     TEXT,
    PRIMARY KEY (objective, region, period, tech, vintage)
);
