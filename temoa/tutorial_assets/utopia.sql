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
INSERT INTO "capacity_factor_process" VALUES('utopia',2000,'inter','day','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2000,'inter','night','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2000,'winter','day','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2000,'winter','night','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2000,'summer','day','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2000,'summer','night','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'inter','day','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'inter','night','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'winter','day','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'winter','night','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'summer','day','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'summer','night','E31',2000,0.2753,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'inter','day','E31',2010,0.2756,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'inter','night','E31',2010,0.2756,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'winter','day','E31',2010,0.2756,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'winter','night','E31',2010,0.2756,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'summer','day','E31',2010,0.2756,'');
INSERT INTO "capacity_factor_process" VALUES('utopia',2010,'summer','night','E31',2010,0.2756,'');
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
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'inter','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'winter','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',1990,'summer','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'inter','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'winter','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2000,'summer','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','day','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','night','E01',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','day','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','night','E21',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','day','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','night','E31',0.275,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','day','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','night','E51',0.17,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'inter','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'winter','night','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','day','E70',0.8,'');
INSERT INTO "capacity_factor_tech" VALUES('utopia',2010,'summer','night','E70',0.8,'');
CREATE TABLE capacity_to_activity
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    c2a    REAL,
    units  TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "capacity_to_activity" VALUES('utopia','E01',31.54,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','E21',31.54,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','E31',31.54,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','E51',31.54,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','E70',31.54,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','RHE',1.0,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','RHO',1.0,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','RL1',1.0,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','SRE',1.0,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','TXD',1.0,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','TXE',1.0,'PJ / (GW * year)','');
INSERT INTO "capacity_to_activity" VALUES('utopia','TXG',1.0,'PJ / (GW * year)','');
CREATE TABLE commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES commodity_type (label),
    description TEXT,
    units       TEXT
);
INSERT INTO "commodity" VALUES('ethos','s','# dummy commodity to supply inputs','PJ');
INSERT INTO "commodity" VALUES('DSL','p','# diesel','PJ');
INSERT INTO "commodity" VALUES('ELC','p','# electricity','PJ');
INSERT INTO "commodity" VALUES('FEQ','p','# fossil equivalent','PJ');
INSERT INTO "commodity" VALUES('GSL','p','# gasoline','PJ');
INSERT INTO "commodity" VALUES('HCO','p','# coal','PJ');
INSERT INTO "commodity" VALUES('HYD','p','# water','PJ');
INSERT INTO "commodity" VALUES('OIL','p','# crude oil','PJ');
INSERT INTO "commodity" VALUES('URN','p','# uranium','PJ');
INSERT INTO "commodity" VALUES('co2','e','#CO2 emissions','Mt');
INSERT INTO "commodity" VALUES('nox','e','#NOX emissions','Mt');
INSERT INTO "commodity" VALUES('RH','d','# residential heating','PJ');
INSERT INTO "commodity" VALUES('RL','d','# residential lighting','PJ');
INSERT INTO "commodity" VALUES('TX','d','# transportation','PJ');
CREATE TABLE commodity_type
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO "commodity_type" VALUES('w','waste commodity');
INSERT INTO "commodity_type" VALUES('wa','waste annual commodity');
INSERT INTO "commodity_type" VALUES('wp','waste physical commodity');
INSERT INTO "commodity_type" VALUES('a','annual commodity');
INSERT INTO "commodity_type" VALUES('s','source commodity');
INSERT INTO "commodity_type" VALUES('p','physical commodity');
INSERT INTO "commodity_type" VALUES('e','emissions commodity');
INSERT INTO "commodity_type" VALUES('d','demand commodity');
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
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E01',1960,40.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E01',1970,40.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E01',1980,40.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E01',1990,40.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E01',1970,70.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E01',1980,70.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E01',1990,70.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E01',2000,70.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E01',1980,100.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E01',1990,100.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E01',2000,100.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E01',2010,100.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E21',1990,500.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E21',1990,500.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E21',1990,500.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E21',2000,500.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E21',2000,500.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E21',2010,500.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E31',1980,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E31',1990,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E31',1980,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E31',1990,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E31',2000,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E31',1980,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E31',1990,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E31',2000,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E31',2010,75.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E51',1980,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E51',1990,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E51',1980,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E51',1990,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E51',2000,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E51',1980,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E51',1990,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E51',2000,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E51',2010,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E70',1960,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E70',1970,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E70',1980,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'E70',1990,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E70',1970,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E70',1980,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E70',1990,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'E70',2000,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E70',1980,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E70',1990,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E70',2000,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'E70',2010,30.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'RHO',1970,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'RHO',1980,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'RHO',1990,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'RHO',1980,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'RHO',1990,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'RHO',2000,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'RHO',1990,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'RHO',2000,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'RHO',2010,1.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'RL1',1980,9.46,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'RL1',1990,9.46,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'RL1',2000,9.46,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'RL1',2010,9.46,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXD',1970,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXD',1980,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXD',1990,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXD',1980,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXD',1990,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXD',2000,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'TXD',2000,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'TXD',2010,52.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXE',1990,100.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXE',1990,90.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXE',2000,90.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'TXE',2000,80.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'TXE',2010,80.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXG',1970,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXG',1980,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',1990,'TXG',1990,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXG',1980,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXG',1990,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2000,'TXG',2000,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'TXG',2000,48.0,'Mdollar / (PJ^2 / GW / year)','');
INSERT INTO "cost_fixed" VALUES('utopia',2010,'TXG',2010,48.0,'Mdollar / (PJ^2 / GW / year)','');
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
INSERT INTO "cost_invest" VALUES('utopia','E01',1990,2000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E01',2000,1300.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E01',2010,1200.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E21',1990,5000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E21',2000,5000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E21',2010,5000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E31',1990,3000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E31',2000,3000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E31',2010,3000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E51',1990,900.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E51',2000,900.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E51',2010,900.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E70',1990,1000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E70',2000,1000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','E70',2010,1000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','RHE',1990,90.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','RHE',2000,90.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','RHE',2010,90.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','RHO',1990,100.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','RHO',2000,100.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','RHO',2010,100.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','SRE',1990,100.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','SRE',2000,100.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','SRE',2010,100.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXD',1990,1044.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXD',2000,1044.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXD',2010,1044.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXE',1990,2000.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXE',2000,1750.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXE',2010,1500.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXG',1990,1044.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXG',2000,1044.0,'Mdollar / (PJ^2 / GW)','');
INSERT INTO "cost_invest" VALUES('utopia','TXG',2010,1044.0,'Mdollar / (PJ^2 / GW)','');
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
INSERT INTO "cost_variable" VALUES('utopia',1990,'IMPDSL1',1990,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'IMPDSL1',1990,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'IMPDSL1',1990,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'IMPGSL1',1990,15.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'IMPGSL1',1990,15.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'IMPGSL1',1990,15.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'IMPHCO1',1990,2.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'IMPHCO1',1990,2.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'IMPHCO1',1990,2.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'IMPOIL1',1990,8.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'IMPOIL1',1990,8.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'IMPOIL1',1990,8.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'IMPURN1',1990,2.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'IMPURN1',1990,2.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'IMPURN1',1990,2.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E01',1960,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E01',1970,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E01',1980,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E01',1990,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E01',1970,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E01',1980,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E01',1990,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E01',2000,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E01',1980,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E01',1990,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E01',2000,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E01',2010,0.3,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E21',1990,1.5,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E21',1990,1.5,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E21',1990,1.5,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E21',2000,1.5,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E21',2000,1.5,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E21',2010,1.5,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E70',1960,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E70',1970,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E70',1980,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'E70',1990,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E70',1970,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E70',1980,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E70',1990,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'E70',2000,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E70',1980,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E70',1990,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E70',2000,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'E70',2010,0.4,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',1990,'SRE',1990,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'SRE',1990,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2000,'SRE',2000,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'SRE',1990,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'SRE',2000,10.0,'Mdollar / (PJ)','');
INSERT INTO "cost_variable" VALUES('utopia',2010,'SRE',2010,10.0,'Mdollar / (PJ)','');
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
INSERT INTO "demand" VALUES('utopia',1990,'RH',25.2,'PJ','');
INSERT INTO "demand" VALUES('utopia',2000,'RH',37.8,'PJ','');
INSERT INTO "demand" VALUES('utopia',2010,'RH',56.7,'PJ','');
INSERT INTO "demand" VALUES('utopia',1990,'RL',5.6,'PJ','');
INSERT INTO "demand" VALUES('utopia',2000,'RL',8.4,'PJ','');
INSERT INTO "demand" VALUES('utopia',2010,'RL',12.6,'PJ','');
INSERT INTO "demand" VALUES('utopia',1990,'TX',5.2,'PJ','');
INSERT INTO "demand" VALUES('utopia',2000,'TX',7.8,'PJ','');
INSERT INTO "demand" VALUES('utopia',2010,'TX',11.69,'PJ','');
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
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'inter','day','RH',0.12,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'inter','night','RH',0.06,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'winter','day','RH',0.5467,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'winter','night','RH',0.2733,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'inter','day','RL',0.15,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'inter','night','RL',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'summer','day','RL',0.15,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'summer','night','RL',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'winter','day','RL',0.5,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',1990,'winter','night','RL',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'inter','day','RH',0.12,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'inter','night','RH',0.06,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'winter','day','RH',0.5467,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'winter','night','RH',0.2733,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'inter','day','RL',0.15,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'inter','night','RL',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'summer','day','RL',0.15,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'summer','night','RL',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'winter','day','RL',0.5,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2000,'winter','night','RL',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'inter','day','RH',0.12,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'inter','night','RH',0.06,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'winter','day','RH',0.5467,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'winter','night','RH',0.2733,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'inter','day','RL',0.15,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'inter','night','RL',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'summer','day','RL',0.15,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'summer','night','RL',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'winter','day','RL',0.5,'');
INSERT INTO "demand_specific_distribution" VALUES('utopia',2010,'winter','night','RL',0.1,'');
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
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPDSL1',1990,'DSL',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPGSL1',1990,'GSL',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPHCO1',1990,'HCO',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPOIL1',1990,'OIL',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPURN1',1990,'URN',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPFEQ',1990,'FEQ',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','ethos','IMPHYD',1990,'HYD',1.0,'PJ / (PJ)','');
INSERT INTO "efficiency" VALUES('utopia','HCO','E01',1960,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HCO','E01',1970,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HCO','E01',1980,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HCO','E01',1990,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HCO','E01',2000,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HCO','E01',2010,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','FEQ','E21',1990,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','FEQ','E21',2000,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','FEQ','E21',2010,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','URN','E21',1990,'ELC',0.4,'PJ / (PJ)','# 1/2.5');
INSERT INTO "efficiency" VALUES('utopia','URN','E21',2000,'ELC',0.4,'PJ / (PJ)','# 1/2.5');
INSERT INTO "efficiency" VALUES('utopia','URN','E21',2010,'ELC',0.4,'PJ / (PJ)','# 1/2.5');
INSERT INTO "efficiency" VALUES('utopia','HYD','E31',1980,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HYD','E31',1990,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HYD','E31',2000,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','HYD','E31',2010,'ELC',0.32,'PJ / (PJ)','# 1/3.125');
INSERT INTO "efficiency" VALUES('utopia','DSL','E70',1960,'ELC',0.294,'PJ / (PJ)','# 1/3.4');
INSERT INTO "efficiency" VALUES('utopia','DSL','E70',1970,'ELC',0.294,'PJ / (PJ)','# 1/3.4');
INSERT INTO "efficiency" VALUES('utopia','DSL','E70',1980,'ELC',0.294,'PJ / (PJ)','# 1/3.4');
INSERT INTO "efficiency" VALUES('utopia','DSL','E70',1990,'ELC',0.294,'PJ / (PJ)','# 1/3.4');
INSERT INTO "efficiency" VALUES('utopia','DSL','E70',2000,'ELC',0.294,'PJ / (PJ)','# 1/3.4');
INSERT INTO "efficiency" VALUES('utopia','DSL','E70',2010,'ELC',0.294,'PJ / (PJ)','# 1/3.4');
INSERT INTO "efficiency" VALUES('utopia','ELC','E51',1980,'ELC',0.72,'PJ / (PJ)','# 1/1.3889');
INSERT INTO "efficiency" VALUES('utopia','ELC','E51',1990,'ELC',0.72,'PJ / (PJ)','# 1/1.3889');
INSERT INTO "efficiency" VALUES('utopia','ELC','E51',2000,'ELC',0.72,'PJ / (PJ)','# 1/1.3889');
INSERT INTO "efficiency" VALUES('utopia','ELC','E51',2010,'ELC',0.72,'PJ / (PJ)','# 1/1.3889');
INSERT INTO "efficiency" VALUES('utopia','ELC','RHE',1990,'RH',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','RHE',2000,'RH',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','RHE',2010,'RH',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','RHO',1970,'RH',0.7,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','RHO',1980,'RH',0.7,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','RHO',1990,'RH',0.7,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','RHO',2000,'RH',0.7,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','RHO',2010,'RH',0.7,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','RL1',1980,'RL',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','RL1',1990,'RL',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','RL1',2000,'RL',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','RL1',2010,'RL',1.0,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','OIL','SRE',1990,'DSL',1.0,'PJ / (PJ)','# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO "efficiency" VALUES('utopia','OIL','SRE',2000,'DSL',1.0,'PJ / (PJ)','# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO "efficiency" VALUES('utopia','OIL','SRE',2010,'DSL',1.0,'PJ / (PJ)','# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO "efficiency" VALUES('utopia','OIL','SRE',1990,'GSL',1.0,'PJ / (PJ)','# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO "efficiency" VALUES('utopia','OIL','SRE',2000,'GSL',1.0,'PJ / (PJ)','# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO "efficiency" VALUES('utopia','OIL','SRE',2010,'GSL',1.0,'PJ / (PJ)','# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO "efficiency" VALUES('utopia','DSL','TXD',1970,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','TXD',1980,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','TXD',1990,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','TXD',2000,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','DSL','TXD',2010,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','TXE',1990,'TX',0.827,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','TXE',2000,'TX',0.827,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','ELC','TXE',2010,'TX',0.827,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','GSL','TXG',1970,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','GSL','TXG',1980,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','GSL','TXG',1990,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','GSL','TXG',2000,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
INSERT INTO "efficiency" VALUES('utopia','GSL','TXG',2010,'TX',0.231,'PJ / (PJ)','# direct translation from DMD_EFF');
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
INSERT INTO "emission_activity" VALUES('utopia','co2','ethos','IMPDSL1',1990,'DSL',0.075,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','co2','ethos','IMPGSL1',1990,'GSL',0.075,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','co2','ethos','IMPHCO1',1990,'HCO',8.9e-02,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','co2','ethos','IMPOIL1',1990,'OIL',0.075,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','DSL','TXD',1970,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','DSL','TXD',1980,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','DSL','TXD',1990,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','DSL','TXD',2000,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','DSL','TXD',2010,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','GSL','TXG',1970,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','GSL','TXG',1980,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','GSL','TXG',1990,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','GSL','TXG',2000,'TX',1.0,'Mt / (PJ)','');
INSERT INTO "emission_activity" VALUES('utopia','nox','GSL','TXG',2010,'TX',1.0,'Mt / (PJ)','');
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
INSERT INTO "existing_capacity" VALUES('utopia','E01',1960,0.175,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E01',1970,0.175,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E01',1980,0.15,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E31',1980,0.1,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E51',1980,0.5,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E70',1960,0.05,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E70',1970,0.05,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','E70',1980,0.2,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','RHO',1970,12.5,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','RHO',1980,12.5,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','RL1',1980,5.6,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','TXD',1970,0.4,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','TXD',1980,0.2,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','TXG',1970,3.1,'GW','');
INSERT INTO "existing_capacity" VALUES('utopia','TXG',1980,1.5,'GW','');
CREATE TABLE lifetime_process
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
INSERT INTO "lifetime_process" VALUES('utopia','RL1',1980,20.0,'year','#forexistingcap');
INSERT INTO "lifetime_process" VALUES('utopia','TXD',1970,30.0,'year','#forexistingcap');
INSERT INTO "lifetime_process" VALUES('utopia','TXD',1980,30.0,'year','#forexistingcap');
INSERT INTO "lifetime_process" VALUES('utopia','TXG',1970,30.0,'year','#forexistingcap');
INSERT INTO "lifetime_process" VALUES('utopia','TXG',1980,30.0,'year','#forexistingcap');
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
CREATE TABLE lifetime_tech
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    lifetime REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "lifetime_tech" VALUES('utopia','E01',40.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','E21',40.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','E31',100.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','E51',100.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','E70',40.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','RHE',30.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','RHO',30.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','RL1',10.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','SRE',50.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','TXD',15.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','TXE',15.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','TXG',15.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPDSL1',1000.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPGSL1',1000.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPHCO1',1000.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPOIL1',1000.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPURN1',1000.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPHYD',1000.0,'year','');
INSERT INTO "lifetime_tech" VALUES('utopia','IMPFEQ',1000.0,'year','');
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
INSERT INTO "limit_capacity" VALUES('utopia',1990,'E31','ge',0.13,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',2000,'E31','ge',0.13,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',2010,'E31','ge',0.13,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',1990,'SRE','ge',0.1,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',1990,'E31','le',0.13,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',2000,'E31','le',0.17,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',2010,'E31','le',2.1e-01,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',1990,'RHE','le',0.0,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',1990,'TXD','le',0.6,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',2000,'TXD','le',1.76,'GW','');
INSERT INTO "limit_capacity" VALUES('utopia',2010,'TXD','le',4.76,'GW','');
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
INSERT INTO "limit_tech_output_split" VALUES('utopia',1990,'SRE','DSL','ge',0.7,'');
INSERT INTO "limit_tech_output_split" VALUES('utopia',2000,'SRE','DSL','ge',0.7,'');
INSERT INTO "limit_tech_output_split" VALUES('utopia',2010,'SRE','DSL','ge',0.7,'');
INSERT INTO "limit_tech_output_split" VALUES('utopia',1990,'SRE','GSL','ge',0.3,'');
INSERT INTO "limit_tech_output_split" VALUES('utopia',2000,'SRE','GSL','ge',0.3,'');
INSERT INTO "limit_tech_output_split" VALUES('utopia',2010,'SRE','GSL','ge',0.3,'');
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
    units    TEXT,
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
INSERT INTO "metadata_real" VALUES('default_loan_rate',0.05,'Default Loan Rate if not specified in loan_rate table');
INSERT INTO "metadata_real" VALUES('global_discount_rate',0.05,'');
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
    units    TEXT,
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
    units    TEXT,
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
    units       TEXT,
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
    units     TEXT,
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
    units       TEXT,
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
    units       TEXT,
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
    units    TEXT,
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
    units     TEXT,
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
    units TEXT,
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
INSERT INTO "region" VALUES('utopia',NULL);
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
INSERT INTO "season_label" VALUES('inter',NULL);
INSERT INTO "season_label" VALUES('summer',NULL);
INSERT INTO "season_label" VALUES('winter',NULL);
CREATE TABLE sector_label
(
    sector TEXT PRIMARY KEY,
    notes  TEXT
);
INSERT INTO "sector_label" VALUES('supply',NULL);
INSERT INTO "sector_label" VALUES('electric',NULL);
INSERT INTO "sector_label" VALUES('transport',NULL);
INSERT INTO "sector_label" VALUES('commercial',NULL);
INSERT INTO "sector_label" VALUES('residential',NULL);
INSERT INTO "sector_label" VALUES('industrial',NULL);
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
INSERT INTO "technology" VALUES('IMPDSL1','p','supply','petroleum','',1,0,0,0,0,0,0,0,' imported diesel');
INSERT INTO "technology" VALUES('IMPGSL1','p','supply','petroleum','',1,0,0,0,0,0,0,0,' imported gasoline');
INSERT INTO "technology" VALUES('IMPHCO1','p','supply','coal','',1,0,0,0,0,0,0,0,' imported coal');
INSERT INTO "technology" VALUES('IMPOIL1','p','supply','petroleum','',1,0,0,0,0,0,0,0,' imported crude oil');
INSERT INTO "technology" VALUES('IMPURN1','p','supply','nuclear','',1,0,0,0,0,0,0,0,' imported uranium');
INSERT INTO "technology" VALUES('IMPFEQ','p','supply','petroleum','',1,0,0,0,0,0,0,0,' imported fossil equivalent');
INSERT INTO "technology" VALUES('IMPHYD','p','supply','hydro','',1,0,0,0,0,0,0,0,' imported water -- doesnt exist in Utopia');
INSERT INTO "technology" VALUES('E01','pb','electric','coal','',0,0,0,0,0,0,0,0,' coal power plant');
INSERT INTO "technology" VALUES('E21','pb','electric','nuclear','',0,0,0,0,0,0,0,0,' nuclear power plant');
INSERT INTO "technology" VALUES('E31','pb','electric','hydro','',0,0,0,0,0,0,0,0,' hydro power');
INSERT INTO "technology" VALUES('E51','ps','electric','electric','',0,0,0,0,0,0,0,0,' electric storage');
INSERT INTO "technology" VALUES('E70','p','electric','petroleum','',0,0,0,0,0,0,0,0,' diesel power plant');
INSERT INTO "technology" VALUES('RHE','p','residential','electric','',0,0,0,0,0,0,0,0,' electric residential heating');
INSERT INTO "technology" VALUES('RHO','p','residential','petroleum','',0,0,0,0,0,0,0,0,' diesel residential heating');
INSERT INTO "technology" VALUES('RL1','p','residential','electric','',0,0,0,0,0,0,0,0,' residential lighting');
INSERT INTO "technology" VALUES('SRE','p','supply','petroleum','',0,0,0,0,0,0,0,0,' crude oil processor');
INSERT INTO "technology" VALUES('TXD','p','transport','petroleum','',0,0,0,0,0,0,0,0,' diesel powered vehicles');
INSERT INTO "technology" VALUES('TXE','p','transport','electric','',0,0,0,0,0,0,0,0,' electric powered vehicles');
INSERT INTO "technology" VALUES('TXG','p','transport','petroleum','',0,0,0,0,0,0,0,0,' gasoline powered vehicles');
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
INSERT INTO "time_of_day" VALUES(1,'day');
INSERT INTO "time_of_day" VALUES(2,'night');
CREATE TABLE time_period
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES time_period_type (label)
);
INSERT INTO "time_period" VALUES(1,1960,'e');
INSERT INTO "time_period" VALUES(2,1970,'e');
INSERT INTO "time_period" VALUES(3,1980,'e');
INSERT INTO "time_period" VALUES(4,1990,'f');
INSERT INTO "time_period" VALUES(5,2000,'f');
INSERT INTO "time_period" VALUES(6,2010,'f');
INSERT INTO "time_period" VALUES(7,2020,'f');
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
INSERT INTO "time_season" VALUES(1990,1,'inter',NULL);
INSERT INTO "time_season" VALUES(1990,2,'summer',NULL);
INSERT INTO "time_season" VALUES(1990,3,'winter',NULL);
INSERT INTO "time_season" VALUES(2000,1,'inter',NULL);
INSERT INTO "time_season" VALUES(2000,2,'summer',NULL);
INSERT INTO "time_season" VALUES(2000,3,'winter',NULL);
INSERT INTO "time_season" VALUES(2010,1,'inter',NULL);
INSERT INTO "time_season" VALUES(2010,2,'summer',NULL);
INSERT INTO "time_season" VALUES(2010,3,'winter',NULL);
CREATE TABLE time_season_all
(
    period INTEGER
        REFERENCES time_period (period),
    sequence INTEGER,
    season TEXT
        REFERENCES season_label (season),
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
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
CREATE TABLE time_season_to_sequential
(
    period INTEGER
        REFERENCES time_period (period),
    sequence INTEGER,
    seas_seq TEXT,
    season TEXT
        REFERENCES season_label (season),
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
INSERT INTO "time_segment_fraction" VALUES(1990,'inter','day',0.1667,'# I-D');
INSERT INTO "time_segment_fraction" VALUES(1990,'inter','night',0.0833,'# I-N');
INSERT INTO "time_segment_fraction" VALUES(1990,'summer','day',0.1667,'# S-D');
INSERT INTO "time_segment_fraction" VALUES(1990,'summer','night',0.0833,'# S-N');
INSERT INTO "time_segment_fraction" VALUES(1990,'winter','day',0.3333,'# W-D');
INSERT INTO "time_segment_fraction" VALUES(1990,'winter','night',0.1667,'# W-N');
INSERT INTO "time_segment_fraction" VALUES(2000,'inter','day',0.1667,'# I-D');
INSERT INTO "time_segment_fraction" VALUES(2000,'inter','night',0.0833,'# I-N');
INSERT INTO "time_segment_fraction" VALUES(2000,'summer','day',0.1667,'# S-D');
INSERT INTO "time_segment_fraction" VALUES(2000,'summer','night',0.0833,'# S-N');
INSERT INTO "time_segment_fraction" VALUES(2000,'winter','day',0.3333,'# W-D');
INSERT INTO "time_segment_fraction" VALUES(2000,'winter','night',0.1667,'# W-N');
INSERT INTO "time_segment_fraction" VALUES(2010,'inter','day',0.1667,'# I-D');
INSERT INTO "time_segment_fraction" VALUES(2010,'inter','night',0.0833,'# I-N');
INSERT INTO "time_segment_fraction" VALUES(2010,'summer','day',0.1667,'# S-D');
INSERT INTO "time_segment_fraction" VALUES(2010,'summer','night',0.0833,'# S-N');
INSERT INTO "time_segment_fraction" VALUES(2010,'winter','day',0.3333,'# W-D');
INSERT INTO "time_segment_fraction" VALUES(2010,'winter','night',0.1667,'# W-N');
CREATE INDEX region_tech_vintage ON myopic_efficiency (region, tech, vintage);
COMMIT;
