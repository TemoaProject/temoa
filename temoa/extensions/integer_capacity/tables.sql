CREATE TABLE IF NOT EXISTS limit_integer_new_capacity(
    region        TEXT,
    tech_or_group TEXT,
    capacity      REAL NOT NULL DEFAULT 0,
    units         TEXT,
    notes         TEXT,
    PRIMARY KEY (region, tech_or_group)
);
CREATE TABLE IF NOT EXISTS limit_integer_net_capacity(
    region        TEXT,
    tech_or_group TEXT,
    capacity      REAL NOT NULL DEFAULT 0,
    units         TEXT,
    notes         TEXT,
    PRIMARY KEY (region, tech_or_group)
);
