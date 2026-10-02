CREATE TABLE IF NOT EXISTS cost_invest_eos
(
	region TEXT NOT NULL,
	tech_or_group TEXT NOT NULL,
	segment INTEGER NOT NULL,
	capacity_lower REAL NOT NULL,
	capacity_upper REAL NOT NULL,
	cost_lower REAL NOT NULL,
	cost_upper REAL NOT NULL,
	units TEXT,
	notes TEXT,
	CHECK (capacity_lower >= 0),
	CHECK (capacity_upper >= 0),
	CHECK (cost_lower >= 0),
	CHECK (cost_upper >= 0),
	PRIMARY KEY (region, tech_or_group, segment)
);
CREATE TABLE IF NOT EXISTS cost_fixed_eos
(
	region TEXT NOT NULL,
	period INTEGER NOT NULL,
	tech_or_group TEXT NOT NULL,
	segment INTEGER NOT NULL,
	capacity_lower REAL NOT NULL,
	capacity_upper REAL NOT NULL,
	cost_lower REAL NOT NULL,
	cost_upper REAL NOT NULL,
	units TEXT,
	notes TEXT,
	CHECK (capacity_lower >= 0),
	CHECK (capacity_upper >= 0),
	CHECK (cost_lower >= 0),
	CHECK (cost_upper >= 0),
	PRIMARY KEY (region, period, tech_or_group, segment)
);
CREATE TABLE IF NOT EXISTS cost_variable_eos
(
	region TEXT NOT NULL,
	period INTEGER NOT NULL,
	tech_or_group TEXT NOT NULL,
	segment INTEGER NOT NULL,
	activity_lower REAL NOT NULL,
	activity_upper REAL NOT NULL,
	cost_lower REAL NOT NULL,
	cost_upper REAL NOT NULL,
	units TEXT,
	notes TEXT,
	CHECK (activity_lower >= 0),
	CHECK (activity_upper >= 0),
	CHECK (cost_lower >= 0),
	CHECK (cost_upper >= 0),
	PRIMARY KEY (region, period, tech_or_group, segment)
);
