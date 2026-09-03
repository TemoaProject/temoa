-- TEMPLATE: Schema for the template extension's owned tables.
-- One CREATE TABLE per entry in ``owned_tables`` (see extension.py). Use
-- ``IF NOT EXISTS`` so the schema can be appended to an existing database when
-- the extension is enabled but its tables are missing.

CREATE TABLE IF NOT EXISTS example_new_capacity_limit
(
    region        TEXT,
    tech_or_group TEXT,
    value         REAL NOT NULL DEFAULT 0,
    units         TEXT,
    notes         TEXT,
    PRIMARY KEY (region, tech_or_group)
);
