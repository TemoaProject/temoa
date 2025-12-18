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
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'spring','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'spring','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'summer','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'summer','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'fall','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'fall','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'winter','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2020,'winter','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'spring','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'spring','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'summer','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'summer','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'fall','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'fall','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'winter','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2020,'winter','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'spring','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'spring','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'summer','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'summer','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'fall','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'fall','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'winter','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2025,'winter','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'spring','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'spring','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'summer','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'summer','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'fall','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'fall','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'winter','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2025,'winter','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'spring','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'spring','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'summer','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'summer','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'fall','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'fall','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'winter','day','E_SOLPV',0.6,'');
INSERT INTO "capacity_factor_tech" VALUES('R1',2030,'winter','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'spring','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'spring','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'summer','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'summer','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'fall','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'fall','night','E_SOLPV',0.0,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'winter','day','E_SOLPV',0.48,'');
INSERT INTO "capacity_factor_tech" VALUES('R2',2030,'winter','night','E_SOLPV',0.0,'');
CREATE TABLE capacity_to_activity
(
    region TEXT,
    tech   TEXT
        REFERENCES technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "capacity_to_activity" VALUES('R1','S_IMPETH',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','S_IMPOIL',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','S_IMPNG',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','S_IMPURN',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','S_OILREF',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','E_NGCC',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R1','E_SOLPV',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R1','E_BATT',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R1','E_NUCLEAR',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R1','T_BLND',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','T_DSL',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','T_GSL',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','T_EV',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','R_EH',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1','R_NGH',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','S_IMPETH',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','S_IMPOIL',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','S_IMPNG',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','S_IMPURN',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','S_OILREF',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','E_NGCC',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R2','E_SOLPV',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R2','E_BATT',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R2','E_NUCLEAR',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R2','T_BLND',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','T_DSL',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','T_GSL',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','T_EV',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','R_EH',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R2','R_NGH',1.0,'');
INSERT INTO "capacity_to_activity" VALUES('R1-R2','E_TRANS',31.54,'');
INSERT INTO "capacity_to_activity" VALUES('R2-R1','E_TRANS',31.54,'');
CREATE TABLE commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES commodity_type (label),
    description TEXT
);
INSERT INTO "commodity" VALUES('ethos','s','dummy commodity to supply inputs (makes graph easier to read)');
INSERT INTO "commodity" VALUES('OIL','p','crude oil');
INSERT INTO "commodity" VALUES('NG','p','natural gas');
INSERT INTO "commodity" VALUES('URN','p','uranium');
INSERT INTO "commodity" VALUES('ETH','p','ethanol');
INSERT INTO "commodity" VALUES('SOL','p','solar insolation');
INSERT INTO "commodity" VALUES('GSL','p','gasoline');
INSERT INTO "commodity" VALUES('DSL','p','diesel');
INSERT INTO "commodity" VALUES('ELC','p','electricity');
INSERT INTO "commodity" VALUES('E10','p','gasoline blend with 10% ethanol');
INSERT INTO "commodity" VALUES('VMT','d','travel demand for vehicle-miles traveled');
INSERT INTO "commodity" VALUES('RH','d','demand for residential heating');
INSERT INTO "commodity" VALUES('CO2','e','CO2 emissions commodity');
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
INSERT INTO "cost_fixed" VALUES('R1',2020,'E_NGCC',2020,30.6,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_NGCC',2020,9.78,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_NGCC',2025,9.78,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_NGCC',2020,9.78,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_NGCC',2025,9.78,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_NGCC',2030,9.78,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2020,'E_SOLPV',2020,10.4,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_SOLPV',2020,10.4,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_SOLPV',2025,9.1,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_SOLPV',2020,10.4,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_SOLPV',2025,9.1,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_SOLPV',2030,9.1,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2020,'E_NUCLEAR',2020,9.809999999999998e+01,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_NUCLEAR',2020,9.809999999999998e+01,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_NUCLEAR',2025,9.809999999999998e+01,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_NUCLEAR',2020,9.809999999999998e+01,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_NUCLEAR',2025,9.809999999999998e+01,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_NUCLEAR',2030,9.809999999999998e+01,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2020,'E_BATT',2020,7.05,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_BATT',2020,7.05,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2025,'E_BATT',2025,7.05,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_BATT',2020,7.05,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_BATT',2025,7.05,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R1',2030,'E_BATT',2030,7.05,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2020,'E_NGCC',2020,24.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_NGCC',2020,7.824,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_NGCC',2025,7.824,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_NGCC',2020,7.824,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_NGCC',2025,7.824,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_NGCC',2030,7.824,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2020,'E_SOLPV',2020,8.32,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_SOLPV',2020,8.32,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_SOLPV',2025,7.28,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_SOLPV',2020,8.32,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_SOLPV',2025,7.28,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_SOLPV',2030,7.28,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2020,'E_NUCLEAR',2020,78.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_NUCLEAR',2020,78.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_NUCLEAR',2025,78.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_NUCLEAR',2020,78.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_NUCLEAR',2025,78.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_NUCLEAR',2030,78.48,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2020,'E_BATT',2020,5.64,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_BATT',2020,5.64,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2025,'E_BATT',2025,5.64,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_BATT',2020,5.64,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_BATT',2025,5.64,'$M/GWyr','');
INSERT INTO "cost_fixed" VALUES('R2',2030,'E_BATT',2030,5.64,'$M/GWyr','');
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
INSERT INTO "cost_invest" VALUES('R1','E_NGCC',2020,1050.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_NGCC',2025,1025.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_NGCC',2030,1000.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_SOLPV',2020,900.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_SOLPV',2025,560.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_SOLPV',2030,800.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_NUCLEAR',2020,6145.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_NUCLEAR',2025,6045.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_NUCLEAR',2030,5890.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_BATT',2020,1150.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_BATT',2025,720.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','E_BATT',2030,480.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R1','T_GSL',2020,2570.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_GSL',2025,2700.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_GSL',2030,2700.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_DSL',2020,2715.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_DSL',2025,2810.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_DSL',2030,2810.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_EV',2020,3100.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_EV',2025,3030.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','T_EV',2030,2925.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R1','R_EH',2020,4.1,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R1','R_EH',2025,4.1,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R1','R_EH',2030,4.1,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R1','R_NGH',2020,7.6,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R1','R_NGH',2025,7.6,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R1','R_NGH',2030,7.6,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R2','E_NGCC',2020,840.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_NGCC',2025,820.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_NGCC',2030,800.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_SOLPV',2020,720.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_SOLPV',2025,448.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_SOLPV',2030,640.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_NUCLEAR',2020,4916.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_NUCLEAR',2025,4836.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_NUCLEAR',2030,4712.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_BATT',2020,920.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_BATT',2025,576.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','E_BATT',2030,384.0,'$M/GW','');
INSERT INTO "cost_invest" VALUES('R2','T_GSL',2020,2056.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_GSL',2025,2160.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_GSL',2030,2160.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_DSL',2020,2172.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_DSL',2025,2248.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_DSL',2030,2248.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_EV',2020,2480.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_EV',2025,2424.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','T_EV',2030,2340.0,'$/bvmt/yr','');
INSERT INTO "cost_invest" VALUES('R2','R_EH',2020,3.28,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R2','R_EH',2025,3.28,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R2','R_EH',2030,3.28,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R2','R_NGH',2020,6.08,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R2','R_NGH',2025,6.08,'$/PJ/yr','');
INSERT INTO "cost_invest" VALUES('R2','R_NGH',2030,6.08,'$/PJ/yr','');
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
INSERT INTO "cost_variable" VALUES('R1',2020,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2020,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2020,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2020,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2020,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'E_NGCC',2025,1.7,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'E_NGCC',2020,1.6,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'E_NGCC',2025,1.7,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'E_NGCC',2030,1.8,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2020,'E_NUCLEAR',2020,0.24,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'E_NUCLEAR',2020,0.24,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2025,'E_NUCLEAR',2025,0.25,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'E_NUCLEAR',2020,0.24,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'E_NUCLEAR',2025,0.25,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1',2030,'E_NUCLEAR',2030,0.26,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2020,'S_IMPETH',2020,25.6,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'S_IMPETH',2020,25.6,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'S_IMPETH',2020,25.6,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2020,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2020,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'S_IMPNG',2020,3.2,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2020,'S_OILREF',2020,0.8,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'S_OILREF',2020,0.8,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'S_OILREF',2020,0.8,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2020,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'E_NGCC',2025,1.36,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'E_NGCC',2020,1.28,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'E_NGCC',2025,1.36,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'E_NGCC',2030,1.44,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2020,'E_NUCLEAR',2020,0.192,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'E_NUCLEAR',2020,0.192,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2025,'E_NUCLEAR',2025,0.2,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'E_NUCLEAR',2020,0.192,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'E_NUCLEAR',2025,0.2,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2',2030,'E_NUCLEAR',2030,2.08000000000000018e-01,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1-R2',2020,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1-R2',2025,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R1-R2',2030,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2-R1',2020,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2-R1',2025,'E_TRANS',2015,0.1,'$M/PJ','');
INSERT INTO "cost_variable" VALUES('R2-R1',2030,'E_TRANS',2015,0.1,'$M/PJ','');
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
INSERT INTO "demand" VALUES('R1',2020,'RH',30.0,'','');
INSERT INTO "demand" VALUES('R1',2025,'RH',33.0,'','');
INSERT INTO "demand" VALUES('R1',2030,'RH',36.0,'','');
INSERT INTO "demand" VALUES('R1',2020,'VMT',84.0,'','');
INSERT INTO "demand" VALUES('R1',2025,'VMT',91.0,'','');
INSERT INTO "demand" VALUES('R1',2030,'VMT',98.0,'','');
INSERT INTO "demand" VALUES('R2',2020,'RH',70.0,'','');
INSERT INTO "demand" VALUES('R2',2025,'RH',77.0,'','');
INSERT INTO "demand" VALUES('R2',2030,'RH',84.0,'','');
INSERT INTO "demand" VALUES('R2',2020,'VMT',36.0,'','');
INSERT INTO "demand" VALUES('R2',2025,'VMT',39.0,'','');
INSERT INTO "demand" VALUES('R2',2030,'VMT',42.0,'','');
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
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'spring','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'spring','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'summer','day','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'summer','night','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'fall','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'fall','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'winter','day','RH',0.3,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2020,'winter','night','RH',0.4,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'spring','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'spring','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'summer','day','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'summer','night','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'fall','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'fall','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'winter','day','RH',0.3,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2020,'winter','night','RH',0.4,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'spring','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'spring','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'summer','day','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'summer','night','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'fall','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'fall','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'winter','day','RH',0.3,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2025,'winter','night','RH',0.4,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'spring','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'spring','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'summer','day','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'summer','night','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'fall','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'fall','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'winter','day','RH',0.3,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2025,'winter','night','RH',0.4,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'spring','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'spring','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'summer','day','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'summer','night','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'fall','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'fall','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'winter','day','RH',0.3,'');
INSERT INTO "demand_specific_distribution" VALUES('R1',2030,'winter','night','RH',0.4,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'spring','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'spring','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'summer','day','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'summer','night','RH',0.0,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'fall','day','RH',0.05,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'fall','night','RH',0.1,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'winter','day','RH',0.3,'');
INSERT INTO "demand_specific_distribution" VALUES('R2',2030,'winter','night','RH',0.4,'');
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
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
INSERT INTO "efficiency" VALUES('R1','ethos','S_IMPETH',2020,'ETH',1.0,'');
INSERT INTO "efficiency" VALUES('R1','ethos','S_IMPOIL',2020,'OIL',1.0,'');
INSERT INTO "efficiency" VALUES('R1','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO "efficiency" VALUES('R1','ethos','S_IMPURN',2020,'URN',1.0,'');
INSERT INTO "efficiency" VALUES('R1','OIL','S_OILREF',2020,'GSL',1.0,'');
INSERT INTO "efficiency" VALUES('R1','OIL','S_OILREF',2020,'DSL',1.0,'');
INSERT INTO "efficiency" VALUES('R1','ETH','T_BLND',2020,'E10',1.0,'');
INSERT INTO "efficiency" VALUES('R1','GSL','T_BLND',2020,'E10',1.0,'');
INSERT INTO "efficiency" VALUES('R1','NG','E_NGCC',2020,'ELC',0.55,'');
INSERT INTO "efficiency" VALUES('R1','NG','E_NGCC',2025,'ELC',0.55,'');
INSERT INTO "efficiency" VALUES('R1','NG','E_NGCC',2030,'ELC',0.55,'');
INSERT INTO "efficiency" VALUES('R1','SOL','E_SOLPV',2020,'ELC',1.0,'');
INSERT INTO "efficiency" VALUES('R1','SOL','E_SOLPV',2025,'ELC',1.0,'');
INSERT INTO "efficiency" VALUES('R1','SOL','E_SOLPV',2030,'ELC',1.0,'');
INSERT INTO "efficiency" VALUES('R1','URN','E_NUCLEAR',2015,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R1','URN','E_NUCLEAR',2020,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R1','URN','E_NUCLEAR',2025,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R1','URN','E_NUCLEAR',2030,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R1','ELC','E_BATT',2020,'ELC',0.85,'');
INSERT INTO "efficiency" VALUES('R1','ELC','E_BATT',2025,'ELC',0.85,'');
INSERT INTO "efficiency" VALUES('R1','ELC','E_BATT',2030,'ELC',0.85,'');
INSERT INTO "efficiency" VALUES('R1','E10','T_GSL',2020,'VMT',0.25,'');
INSERT INTO "efficiency" VALUES('R1','E10','T_GSL',2025,'VMT',0.25,'');
INSERT INTO "efficiency" VALUES('R1','E10','T_GSL',2030,'VMT',0.25,'');
INSERT INTO "efficiency" VALUES('R1','DSL','T_DSL',2020,'VMT',0.3,'');
INSERT INTO "efficiency" VALUES('R1','DSL','T_DSL',2025,'VMT',0.3,'');
INSERT INTO "efficiency" VALUES('R1','DSL','T_DSL',2030,'VMT',0.3,'');
INSERT INTO "efficiency" VALUES('R1','ELC','T_EV',2020,'VMT',0.89,'');
INSERT INTO "efficiency" VALUES('R1','ELC','T_EV',2025,'VMT',0.89,'');
INSERT INTO "efficiency" VALUES('R1','ELC','T_EV',2030,'VMT',0.89,'');
INSERT INTO "efficiency" VALUES('R1','ELC','R_EH',2020,'RH',1.0,'');
INSERT INTO "efficiency" VALUES('R1','ELC','R_EH',2025,'RH',1.0,'');
INSERT INTO "efficiency" VALUES('R1','ELC','R_EH',2030,'RH',1.0,'');
INSERT INTO "efficiency" VALUES('R1','NG','R_NGH',2020,'RH',0.85,'');
INSERT INTO "efficiency" VALUES('R1','NG','R_NGH',2025,'RH',0.85,'');
INSERT INTO "efficiency" VALUES('R1','NG','R_NGH',2030,'RH',0.85,'');
INSERT INTO "efficiency" VALUES('R2','ethos','S_IMPETH',2020,'ETH',1.0,'');
INSERT INTO "efficiency" VALUES('R2','ethos','S_IMPOIL',2020,'OIL',1.0,'');
INSERT INTO "efficiency" VALUES('R2','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO "efficiency" VALUES('R2','ethos','S_IMPURN',2020,'URN',1.0,'');
INSERT INTO "efficiency" VALUES('R2','OIL','S_OILREF',2020,'GSL',1.0,'');
INSERT INTO "efficiency" VALUES('R2','OIL','S_OILREF',2020,'DSL',1.0,'');
INSERT INTO "efficiency" VALUES('R2','ETH','T_BLND',2020,'E10',1.0,'');
INSERT INTO "efficiency" VALUES('R2','GSL','T_BLND',2020,'E10',1.0,'');
INSERT INTO "efficiency" VALUES('R2','NG','E_NGCC',2020,'ELC',0.55,'');
INSERT INTO "efficiency" VALUES('R2','NG','E_NGCC',2025,'ELC',0.55,'');
INSERT INTO "efficiency" VALUES('R2','NG','E_NGCC',2030,'ELC',0.55,'');
INSERT INTO "efficiency" VALUES('R2','SOL','E_SOLPV',2020,'ELC',1.0,'');
INSERT INTO "efficiency" VALUES('R2','SOL','E_SOLPV',2025,'ELC',1.0,'');
INSERT INTO "efficiency" VALUES('R2','SOL','E_SOLPV',2030,'ELC',1.0,'');
INSERT INTO "efficiency" VALUES('R2','URN','E_NUCLEAR',2015,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R2','URN','E_NUCLEAR',2020,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R2','URN','E_NUCLEAR',2025,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R2','URN','E_NUCLEAR',2030,'ELC',0.4,'');
INSERT INTO "efficiency" VALUES('R2','ELC','E_BATT',2020,'ELC',0.85,'');
INSERT INTO "efficiency" VALUES('R2','ELC','E_BATT',2025,'ELC',0.85,'');
INSERT INTO "efficiency" VALUES('R2','ELC','E_BATT',2030,'ELC',0.85,'');
INSERT INTO "efficiency" VALUES('R2','E10','T_GSL',2020,'VMT',0.25,'');
INSERT INTO "efficiency" VALUES('R2','E10','T_GSL',2025,'VMT',0.25,'');
INSERT INTO "efficiency" VALUES('R2','E10','T_GSL',2030,'VMT',0.25,'');
INSERT INTO "efficiency" VALUES('R2','DSL','T_DSL',2020,'VMT',0.3,'');
INSERT INTO "efficiency" VALUES('R2','DSL','T_DSL',2025,'VMT',0.3,'');
INSERT INTO "efficiency" VALUES('R2','DSL','T_DSL',2030,'VMT',0.3,'');
INSERT INTO "efficiency" VALUES('R2','ELC','T_EV',2020,'VMT',0.89,'');
INSERT INTO "efficiency" VALUES('R2','ELC','T_EV',2025,'VMT',0.89,'');
INSERT INTO "efficiency" VALUES('R2','ELC','T_EV',2030,'VMT',0.89,'');
INSERT INTO "efficiency" VALUES('R2','ELC','R_EH',2020,'RH',1.0,'');
INSERT INTO "efficiency" VALUES('R2','ELC','R_EH',2025,'RH',1.0,'');
INSERT INTO "efficiency" VALUES('R2','ELC','R_EH',2030,'RH',1.0,'');
INSERT INTO "efficiency" VALUES('R2','NG','R_NGH',2020,'RH',0.85,'');
INSERT INTO "efficiency" VALUES('R2','NG','R_NGH',2025,'RH',0.85,'');
INSERT INTO "efficiency" VALUES('R2','NG','R_NGH',2030,'RH',0.85,'');
INSERT INTO "efficiency" VALUES('R1-R2','ELC','E_TRANS',2015,'ELC',0.9,'');
INSERT INTO "efficiency" VALUES('R2-R1','ELC','E_TRANS',2015,'ELC',0.9,'');
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
INSERT INTO "emission_activity" VALUES('R1','CO2','ethos','S_IMPNG',2020,'NG',5.029999999999999e+01,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "emission_activity" VALUES('R1','CO2','OIL','S_OILREF',2020,'GSL',67.2,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "emission_activity" VALUES('R1','CO2','OIL','S_OILREF',2020,'DSL',69.4,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "emission_activity" VALUES('R2','CO2','ethos','S_IMPNG',2020,'NG',5.029999999999999e+01,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "emission_activity" VALUES('R2','CO2','OIL','S_OILREF',2020,'GSL',67.2,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO "emission_activity" VALUES('R2','CO2','OIL','S_OILREF',2020,'DSL',69.4,'kT/PJ','taken from MIT Energy Fact Sheet');
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
INSERT INTO "existing_capacity" VALUES('R1','E_NUCLEAR',2015,0.07,'GW','');
INSERT INTO "existing_capacity" VALUES('R2','E_NUCLEAR',2015,0.03,'GW','');
INSERT INTO "existing_capacity" VALUES('R1-R2','E_TRANS',2015,10.0,'GW','');
INSERT INTO "existing_capacity" VALUES('R2-R1','E_TRANS',2015,10.0,'GW','');
CREATE TABLE lifetime_process
(
    region   TEXT,
    tech     TEXT
        REFERENCES technology (tech),
    vintage  INTEGER
        REFERENCES time_period (period),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
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
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO "lifetime_tech" VALUES('R1','S_IMPETH',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','S_IMPOIL',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','S_IMPNG',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','S_IMPURN',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','S_OILREF',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','E_NGCC',30.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','E_SOLPV',30.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','E_BATT',20.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','E_NUCLEAR',50.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','T_BLND',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','T_DSL',12.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','T_GSL',12.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','T_EV',12.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','R_EH',20.0,'');
INSERT INTO "lifetime_tech" VALUES('R1','R_NGH',20.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','S_IMPETH',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','S_IMPOIL',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','S_IMPNG',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','S_IMPURN',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','S_OILREF',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','E_NGCC',30.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','E_SOLPV',30.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','E_BATT',20.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','E_NUCLEAR',50.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','T_BLND',100.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','T_DSL',12.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','T_GSL',12.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','T_EV',12.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','R_EH',20.0,'');
INSERT INTO "lifetime_tech" VALUES('R2','R_NGH',20.0,'');
INSERT INTO "lifetime_tech" VALUES('R1-R2','E_TRANS',30.0,'');
INSERT INTO "lifetime_tech" VALUES('R2-R1','E_TRANS',30.0,'');
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
INSERT INTO "limit_activity" VALUES('R1',2020,'T_GSL','ge',35.0,'','');
INSERT INTO "limit_activity" VALUES('R1',2025,'T_GSL','ge',35.0,'','');
INSERT INTO "limit_activity" VALUES('R1',2030,'T_GSL','ge',35.0,'','');
INSERT INTO "limit_activity" VALUES('R2',2020,'T_GSL','ge',15.0,'','');
INSERT INTO "limit_activity" VALUES('R2',2025,'T_GSL','ge',15.0,'','');
INSERT INTO "limit_activity" VALUES('R2',2030,'T_GSL','ge',15.0,'','');
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
INSERT INTO "limit_emission" VALUES('R1',2020,'CO2','le',25000.0,'kT CO2','');
INSERT INTO "limit_emission" VALUES('R1',2025,'CO2','le',24000.0,'kT CO2','');
INSERT INTO "limit_emission" VALUES('R1',2030,'CO2','le',23000.0,'kT CO2','');
INSERT INTO "limit_emission" VALUES('global',2020,'CO2','le',37500.0,'kT CO2','');
INSERT INTO "limit_emission" VALUES('global',2025,'CO2','le',36000.0,'kT CO2','');
INSERT INTO "limit_emission" VALUES('global',2030,'CO2','le',34500.0,'kT CO2','');
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
INSERT INTO "limit_storage_level_fraction" VALUES('R1',2025,'winter','day','E_BATT',2025,'e',0.5,'');
INSERT INTO "limit_storage_level_fraction" VALUES('R2',2020,'summer','day','E_BATT',2020,'e',0.5,'');
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
INSERT INTO "limit_tech_input_split" VALUES('R1',2020,'GSL','T_BLND','ge',0.9,'');
INSERT INTO "limit_tech_input_split" VALUES('R1',2020,'ETH','T_BLND','ge',0.1,'');
INSERT INTO "limit_tech_input_split" VALUES('R1',2025,'GSL','T_BLND','ge',0.9,'');
INSERT INTO "limit_tech_input_split" VALUES('R1',2025,'ETH','T_BLND','ge',0.1,'');
INSERT INTO "limit_tech_input_split" VALUES('R1',2030,'GSL','T_BLND','ge',0.9,'');
INSERT INTO "limit_tech_input_split" VALUES('R1',2030,'ETH','T_BLND','ge',0.1,'');
INSERT INTO "limit_tech_input_split" VALUES('R2',2020,'GSL','T_BLND','ge',0.72,'');
INSERT INTO "limit_tech_input_split" VALUES('R2',2020,'ETH','T_BLND','ge',0.08,'');
INSERT INTO "limit_tech_input_split" VALUES('R2',2025,'GSL','T_BLND','ge',0.72,'');
INSERT INTO "limit_tech_input_split" VALUES('R2',2025,'ETH','T_BLND','ge',0.08,'');
INSERT INTO "limit_tech_input_split" VALUES('R2',2030,'GSL','T_BLND','ge',0.72,'');
INSERT INTO "limit_tech_input_split" VALUES('R2',2030,'ETH','T_BLND','ge',0.08,'');
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
INSERT INTO "limit_tech_output_split" VALUES('R1',2020,'S_OILREF','GSL','ge',0.9,'');
INSERT INTO "limit_tech_output_split" VALUES('R1',2020,'S_OILREF','DSL','ge',0.1,'');
INSERT INTO "limit_tech_output_split" VALUES('R1',2025,'S_OILREF','GSL','ge',0.9,'');
INSERT INTO "limit_tech_output_split" VALUES('R1',2025,'S_OILREF','DSL','ge',0.1,'');
INSERT INTO "limit_tech_output_split" VALUES('R1',2030,'S_OILREF','GSL','ge',0.9,'');
INSERT INTO "limit_tech_output_split" VALUES('R1',2030,'S_OILREF','DSL','ge',0.1,'');
INSERT INTO "limit_tech_output_split" VALUES('R2',2020,'S_OILREF','GSL','ge',0.72,'');
INSERT INTO "limit_tech_output_split" VALUES('R2',2020,'S_OILREF','DSL','ge',0.08,'');
INSERT INTO "limit_tech_output_split" VALUES('R2',2025,'S_OILREF','GSL','ge',0.72,'');
INSERT INTO "limit_tech_output_split" VALUES('R2',2025,'S_OILREF','DSL','ge',0.08,'');
INSERT INTO "limit_tech_output_split" VALUES('R2',2030,'S_OILREF','GSL','ge',0.72,'');
INSERT INTO "limit_tech_output_split" VALUES('R2',2030,'S_OILREF','DSL','ge',0.08,'');
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
INSERT INTO "region" VALUES('R1',NULL);
INSERT INTO "region" VALUES('R2',NULL);
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
INSERT INTO "season_label" VALUES('summer',NULL);
INSERT INTO "season_label" VALUES('fall',NULL);
INSERT INTO "season_label" VALUES('winter',NULL);
INSERT INTO "season_label" VALUES('spring',NULL);
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
INSERT INTO "storage_duration" VALUES('R1','E_BATT',8.0,'8-hour duration specified as fraction of a day');
INSERT INTO "storage_duration" VALUES('R2','E_BATT',8.0,'8-hour duration specified as fraction of a day');
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
INSERT INTO "technology" VALUES('S_IMPETH','p','supply','','',1,0,0,0,0,0,0,0,' imported ethanol');
INSERT INTO "technology" VALUES('S_IMPOIL','p','supply','','',1,0,0,0,0,0,0,0,' imported crude oil');
INSERT INTO "technology" VALUES('S_IMPNG','p','supply','','',1,0,0,0,0,0,0,0,' imported natural gas');
INSERT INTO "technology" VALUES('S_IMPURN','p','supply','','',1,0,0,0,0,0,0,0,' imported uranium');
INSERT INTO "technology" VALUES('S_OILREF','p','supply','','',0,0,0,1,0,0,0,0,' crude oil refinery');
INSERT INTO "technology" VALUES('E_NGCC','p','electric','','',0,0,0,0,0,0,0,0,' natural gas combined-cycle');
INSERT INTO "technology" VALUES('E_SOLPV','p','electric','','',0,0,0,0,0,0,0,0,' solar photovoltaic');
INSERT INTO "technology" VALUES('E_BATT','ps','electric','','',0,0,0,0,0,0,0,0,' lithium-ion battery');
INSERT INTO "technology" VALUES('E_NUCLEAR','pb','electric','','',0,0,0,0,0,0,0,0,' nuclear power plant');
INSERT INTO "technology" VALUES('T_BLND','p','transport','','',0,0,0,0,0,0,0,0,'ethanol - gasoline blending process');
INSERT INTO "technology" VALUES('T_DSL','p','transport','','',0,0,0,0,0,0,0,0,'diesel vehicle');
INSERT INTO "technology" VALUES('T_GSL','p','transport','','',0,0,0,0,0,0,0,0,'gasoline vehicle');
INSERT INTO "technology" VALUES('T_EV','p','transport','','',0,0,0,0,0,0,0,0,'electric vehicle');
INSERT INTO "technology" VALUES('R_EH','p','residential','','',0,0,0,0,0,0,0,0,' electric residential heating');
INSERT INTO "technology" VALUES('R_NGH','p','residential','','',0,0,0,0,0,0,0,0,' natural gas residential heating');
INSERT INTO "technology" VALUES('E_TRANS','p','electric','','',0,0,0,0,0,0,1,0,'electric transmission');
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
INSERT INTO "time_period" VALUES(1,2015,'e');
INSERT INTO "time_period" VALUES(2,2020,'f');
INSERT INTO "time_period" VALUES(3,2025,'f');
INSERT INTO "time_period" VALUES(4,2030,'f');
INSERT INTO "time_period" VALUES(5,2035,'f');
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
INSERT INTO "time_season" VALUES(2020,1,'spring',NULL);
INSERT INTO "time_season" VALUES(2020,2,'summer',NULL);
INSERT INTO "time_season" VALUES(2020,3,'fall',NULL);
INSERT INTO "time_season" VALUES(2020,4,'winter',NULL);
INSERT INTO "time_season" VALUES(2025,1,'spring',NULL);
INSERT INTO "time_season" VALUES(2025,2,'summer',NULL);
INSERT INTO "time_season" VALUES(2025,3,'fall',NULL);
INSERT INTO "time_season" VALUES(2025,4,'winter',NULL);
INSERT INTO "time_season" VALUES(2030,1,'spring',NULL);
INSERT INTO "time_season" VALUES(2030,2,'summer',NULL);
INSERT INTO "time_season" VALUES(2030,3,'fall',NULL);
INSERT INTO "time_season" VALUES(2030,4,'winter',NULL);

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
INSERT INTO "time_segment_fraction" VALUES(2020,'spring','day',0.125,'Spring - Day');
INSERT INTO "time_segment_fraction" VALUES(2020,'spring','night',0.125,'Spring - Night');
INSERT INTO "time_segment_fraction" VALUES(2020,'summer','day',0.125,'Summer - Day');
INSERT INTO "time_segment_fraction" VALUES(2020,'summer','night',0.125,'Summer - Night');
INSERT INTO "time_segment_fraction" VALUES(2020,'fall','day',0.125,'Fall - Day');
INSERT INTO "time_segment_fraction" VALUES(2020,'fall','night',0.125,'Fall - Night');
INSERT INTO "time_segment_fraction" VALUES(2020,'winter','day',0.125,'Winter - Day');
INSERT INTO "time_segment_fraction" VALUES(2020,'winter','night',0.125,'Winter - Night');
INSERT INTO "time_segment_fraction" VALUES(2025,'spring','day',0.125,'Spring - Day');
INSERT INTO "time_segment_fraction" VALUES(2025,'spring','night',0.125,'Spring - Night');
INSERT INTO "time_segment_fraction" VALUES(2025,'summer','day',0.125,'Summer - Day');
INSERT INTO "time_segment_fraction" VALUES(2025,'summer','night',0.125,'Summer - Night');
INSERT INTO "time_segment_fraction" VALUES(2025,'fall','day',0.125,'Fall - Day');
INSERT INTO "time_segment_fraction" VALUES(2025,'fall','night',0.125,'Fall - Night');
INSERT INTO "time_segment_fraction" VALUES(2025,'winter','day',0.125,'Winter - Day');
INSERT INTO "time_segment_fraction" VALUES(2025,'winter','night',0.125,'Winter - Night');
INSERT INTO "time_segment_fraction" VALUES(2030,'spring','day',0.125,'Spring - Day');
INSERT INTO "time_segment_fraction" VALUES(2030,'spring','night',0.125,'Spring - Night');
INSERT INTO "time_segment_fraction" VALUES(2030,'summer','day',0.125,'Summer - Day');
INSERT INTO "time_segment_fraction" VALUES(2030,'summer','night',0.125,'Summer - Night');
INSERT INTO "time_segment_fraction" VALUES(2030,'fall','day',0.125,'Fall - Day');
INSERT INTO "time_segment_fraction" VALUES(2030,'fall','night',0.125,'Fall - Night');
INSERT INTO "time_segment_fraction" VALUES(2030,'winter','day',0.125,'Winter - Day');
INSERT INTO "time_segment_fraction" VALUES(2030,'winter','night',0.125,'Winter - Night');
CREATE INDEX region_tech_vintage ON myopic_efficiency (region, tech, vintage);
COMMIT;
