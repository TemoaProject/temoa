CREATE TABLE IF NOT EXISTS limit_discrete_new_capacity(
    region        TEXT NOT NULL,
    tech_or_group TEXT NOT NULL,
    capacity      REAL NOT NULL DEFAULT 0,
    units         TEXT,
    notes         TEXT,
    PRIMARY KEY (region, tech_or_group)
);
CREATE TABLE IF NOT EXISTS limit_discrete_capacity(
    region        TEXT NOT NULL,
    tech_or_group TEXT NOT NULL,
    capacity      REAL NOT NULL DEFAULT 0,
    units         TEXT,
    notes         TEXT,
    PRIMARY KEY (region, tech_or_group)
);
