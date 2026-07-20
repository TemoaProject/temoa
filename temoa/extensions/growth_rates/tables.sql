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
