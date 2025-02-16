PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE MetaData
(
    element TEXT,
    value   INT,
    notes   TEXT,
    PRIMARY KEY (element)
);
INSERT INTO MetaData VALUES('myopic_base_year',2000,'Base Year for Myopic Analysis');
INSERT INTO MetaData VALUES('DB_MAJOR',3,'DB major version number');
INSERT INTO MetaData VALUES('DB_MINOR',0,'DB minor version number');
INSERT INTO MetaData VALUES('link_seasons',1,'Carry storage states between seasons');
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05,'Default Loan Rate if not specified in LoanRate table');
INSERT INTO MetaDataReal VALUES('global_discount_rate',0.05,'');
CREATE TABLE OutputDualVariable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
CREATE TABLE OutputObjective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
);
CREATE TABLE SectorLabel
(
    sector TEXT,
    PRIMARY KEY (sector)
);
INSERT INTO SectorLabel VALUES('supply');
INSERT INTO SectorLabel VALUES('electric');
INSERT INTO SectorLabel VALUES('transport');
INSERT INTO SectorLabel VALUES('commercial');
INSERT INTO SectorLabel VALUES('residential');
INSERT INTO SectorLabel VALUES('industrial');
CREATE TABLE CapacityCredit
(
    region  TEXT,
    period  INTEGER,
    tech    TEXT,
    vintage INTEGER,
    credit  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage),
    CHECK (credit >= 0 AND credit <= 1)
);
CREATE TABLE CapacityFactorProcess
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    season  TEXT
        REFERENCES TimeSeason (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, period, season, tod, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE CapacityFactorTech
(
    region TEXT,
    season TEXT
        REFERENCES TimeSeason (season),
    tod    TEXT
        REFERENCES TimeOfDay (tod),
    tech   TEXT
        REFERENCES Technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO CapacityFactorTech VALUES('R1','spring','day','E_SOLPV',0.5999999999999999778,'');
INSERT INTO CapacityFactorTech VALUES('R1','spring','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R1','summer','day','E_SOLPV',0.5999999999999999778,'');
INSERT INTO CapacityFactorTech VALUES('R1','summer','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R1','fall','day','E_SOLPV',0.5999999999999999778,'');
INSERT INTO CapacityFactorTech VALUES('R1','fall','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R1','winter','day','E_SOLPV',0.5999999999999999778,'');
INSERT INTO CapacityFactorTech VALUES('R1','winter','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R2','spring','day','E_SOLPV',0.4799999999999999823,'');
INSERT INTO CapacityFactorTech VALUES('R2','spring','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R2','summer','day','E_SOLPV',0.4799999999999999823,'');
INSERT INTO CapacityFactorTech VALUES('R2','summer','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R2','fall','day','E_SOLPV',0.4799999999999999823,'');
INSERT INTO CapacityFactorTech VALUES('R2','fall','night','E_SOLPV',0.0,'');
INSERT INTO CapacityFactorTech VALUES('R2','winter','day','E_SOLPV',0.4799999999999999823,'');
INSERT INTO CapacityFactorTech VALUES('R2','winter','night','E_SOLPV',0.0,'');
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('R1','S_IMPETH',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','S_IMPOIL',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','S_IMPNG',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','S_IMPURN',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','S_OILREF',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','E_NGCC',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R1','E_SOLPV',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R1','E_BATT',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R1','E_NUCLEAR',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R1','T_BLND',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','T_DSL',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','T_GSL',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','T_EV',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','R_EH',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1','R_NGH',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','S_IMPETH',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','S_IMPOIL',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','S_IMPNG',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','S_IMPURN',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','S_OILREF',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','E_NGCC',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R2','E_SOLPV',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R2','E_BATT',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R2','E_NUCLEAR',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R2','T_BLND',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','T_DSL',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','T_GSL',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','T_EV',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','R_EH',1.0,'');
INSERT INTO CapacityToActivity VALUES('R2','R_NGH',1.0,'');
INSERT INTO CapacityToActivity VALUES('R1-R2','E_TRANS',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('R2-R1','E_TRANS',31.53999999999999915,'');
CREATE TABLE Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
INSERT INTO Commodity VALUES('ethos','s','dummy commodity to supply inputs (makes graph easier to read)');
INSERT INTO Commodity VALUES('OIL','p','crude oil');
INSERT INTO Commodity VALUES('NG','p','natural gas');
INSERT INTO Commodity VALUES('URN','p','uranium');
INSERT INTO Commodity VALUES('ETH','p','ethanol');
INSERT INTO Commodity VALUES('SOL','p','solar insolation');
INSERT INTO Commodity VALUES('GSL','p','gasoline');
INSERT INTO Commodity VALUES('DSL','p','diesel');
INSERT INTO Commodity VALUES('ELC','p','electricity');
INSERT INTO Commodity VALUES('E10','p','gasoline blend with 10% ethanol');
INSERT INTO Commodity VALUES('VMT','d','travel demand for vehicle-miles traveled');
INSERT INTO Commodity VALUES('RH','d','demand for residential heating');
INSERT INTO Commodity VALUES('CO2','e','CO2 emissions commodity');
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO CommodityType VALUES('s','source commodity');
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
CREATE TABLE CostEmission
(
    region    TEXT
        REFERENCES Region (region),
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT NOT NULL
        REFERENCES Commodity (name),
    cost      REAL NOT NULL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm)
);
CREATE TABLE CostFixed
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    tech    TEXT    NOT NULL
        REFERENCES Technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
INSERT INTO CostFixed VALUES('R1',2020,'E_NGCC',2020,30.60000000000000142,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_NGCC',2020,9.77999999999999937,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_NGCC',2025,9.77999999999999937,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_NGCC',2020,9.77999999999999937,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_NGCC',2025,9.77999999999999937,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_NGCC',2030,9.77999999999999937,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2020,'E_SOLPV',2020,10.40000000000000035,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_SOLPV',2020,10.40000000000000035,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_SOLPV',2025,9.099999999999999645,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_SOLPV',2020,10.40000000000000035,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_SOLPV',2025,9.099999999999999645,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_SOLPV',2030,9.099999999999999645,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2020,'E_NUCLEAR',2020,98.0999999999999944,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_NUCLEAR',2020,98.0999999999999944,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_NUCLEAR',2025,98.0999999999999944,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_NUCLEAR',2020,98.0999999999999944,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_NUCLEAR',2025,98.0999999999999944,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_NUCLEAR',2030,98.0999999999999944,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2020,'E_BATT',2020,7.049999999999999823,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_BATT',2020,7.049999999999999823,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2025,'E_BATT',2025,7.049999999999999823,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_BATT',2020,7.049999999999999823,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_BATT',2025,7.049999999999999823,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R1',2030,'E_BATT',2030,7.049999999999999823,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2020,'E_NGCC',2020,24.48000000000000042,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_NGCC',2020,7.823999999999999844,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_NGCC',2025,7.823999999999999844,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_NGCC',2020,7.823999999999999844,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_NGCC',2025,7.823999999999999844,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_NGCC',2030,7.823999999999999844,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2020,'E_SOLPV',2020,8.320000000000000284,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_SOLPV',2020,8.320000000000000284,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_SOLPV',2025,7.280000000000000248,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_SOLPV',2020,8.320000000000000284,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_SOLPV',2025,7.280000000000000248,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_SOLPV',2030,7.280000000000000248,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2020,'E_NUCLEAR',2020,78.48000000000000397,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_NUCLEAR',2020,78.48000000000000397,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_NUCLEAR',2025,78.48000000000000397,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_NUCLEAR',2020,78.48000000000000397,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_NUCLEAR',2025,78.48000000000000397,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_NUCLEAR',2030,78.48000000000000397,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2020,'E_BATT',2020,5.639999999999999681,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_BATT',2020,5.639999999999999681,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2025,'E_BATT',2025,5.639999999999999681,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_BATT',2020,5.639999999999999681,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_BATT',2025,5.639999999999999681,'$M/GWyr','');
INSERT INTO CostFixed VALUES('R2',2030,'E_BATT',2030,5.639999999999999681,'$M/GWyr','');
CREATE TABLE CostInvest
(
    region  TEXT,
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER
        REFERENCES TimePeriod (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech, vintage)
);
INSERT INTO CostInvest VALUES('R1','E_NGCC',2020,1050.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_NGCC',2025,1025.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_NGCC',2030,1000.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_SOLPV',2020,900.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_SOLPV',2025,560.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_SOLPV',2030,800.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_NUCLEAR',2020,6145.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_NUCLEAR',2025,6045.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_NUCLEAR',2030,5890.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_BATT',2020,1150.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_BATT',2025,720.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','E_BATT',2030,480.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R1','T_GSL',2020,2570.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_GSL',2025,2700.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_GSL',2030,2700.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_DSL',2020,2715.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_DSL',2025,2810.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_DSL',2030,2810.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_EV',2020,3100.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_EV',2025,3030.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','T_EV',2030,2925.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R1','R_EH',2020,4.099999999999999644,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R1','R_EH',2025,4.099999999999999644,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R1','R_EH',2030,4.099999999999999644,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R1','R_NGH',2020,7.599999999999999645,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R1','R_NGH',2025,7.599999999999999645,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R1','R_NGH',2030,7.599999999999999645,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R2','E_NGCC',2020,840.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_NGCC',2025,820.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_NGCC',2030,800.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_SOLPV',2020,720.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_SOLPV',2025,448.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_SOLPV',2030,640.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_NUCLEAR',2020,4916.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_NUCLEAR',2025,4836.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_NUCLEAR',2030,4712.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_BATT',2020,920.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_BATT',2025,576.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','E_BATT',2030,384.0,'$M/GW','');
INSERT INTO CostInvest VALUES('R2','T_GSL',2020,2056.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_GSL',2025,2160.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_GSL',2030,2160.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_DSL',2020,2172.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_DSL',2025,2248.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_DSL',2030,2248.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_EV',2020,2480.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_EV',2025,2424.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','T_EV',2030,2340.0,'$/bvmt/yr','');
INSERT INTO CostInvest VALUES('R2','R_EH',2020,3.279999999999999805,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R2','R_EH',2025,3.279999999999999805,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R2','R_EH',2030,3.279999999999999805,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R2','R_NGH',2020,6.080000000000000071,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R2','R_NGH',2025,6.080000000000000071,'$/PJ/yr','');
INSERT INTO CostInvest VALUES('R2','R_NGH',2030,6.080000000000000071,'$/PJ/yr','');
CREATE TABLE CostVariable
(
    region  TEXT    NOT NULL,
    period  INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    tech    TEXT    NOT NULL
        REFERENCES Technology (tech),
    vintage INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    cost    REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech, vintage)
);
INSERT INTO CostVariable VALUES('R1',2020,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'S_IMPETH',2020,32.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2020,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'S_IMPOIL',2020,20.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2020,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'S_IMPNG',2020,4.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2020,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'S_OILREF',2020,1.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2020,'E_NGCC',2020,1.600000000000000088,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'E_NGCC',2020,1.600000000000000088,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'E_NGCC',2025,1.699999999999999956,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'E_NGCC',2020,1.600000000000000088,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'E_NGCC',2025,1.699999999999999956,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'E_NGCC',2030,1.800000000000000044,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2020,'E_NUCLEAR',2020,0.2399999999999999912,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'E_NUCLEAR',2020,0.2399999999999999912,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2025,'E_NUCLEAR',2025,0.25,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'E_NUCLEAR',2020,0.2399999999999999912,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'E_NUCLEAR',2025,0.25,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1',2030,'E_NUCLEAR',2030,0.2600000000000000088,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2020,'S_IMPETH',2020,25.60000000000000142,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'S_IMPETH',2020,25.60000000000000142,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'S_IMPETH',2020,25.60000000000000142,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2020,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'S_IMPOIL',2020,16.0,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2020,'S_IMPNG',2020,3.200000000000000177,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'S_IMPNG',2020,3.200000000000000177,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'S_IMPNG',2020,3.200000000000000177,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2020,'S_OILREF',2020,0.8000000000000000444,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'S_OILREF',2020,0.8000000000000000444,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'S_OILREF',2020,0.8000000000000000444,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2020,'E_NGCC',2020,1.280000000000000026,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'E_NGCC',2020,1.280000000000000026,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'E_NGCC',2025,1.360000000000000097,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'E_NGCC',2020,1.280000000000000026,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'E_NGCC',2025,1.360000000000000097,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'E_NGCC',2030,1.439999999999999947,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2020,'E_NUCLEAR',2020,0.1920000000000000039,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'E_NUCLEAR',2020,0.1920000000000000039,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2025,'E_NUCLEAR',2025,0.2000000000000000111,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'E_NUCLEAR',2020,0.1920000000000000039,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'E_NUCLEAR',2025,0.2000000000000000111,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2',2030,'E_NUCLEAR',2030,0.2079999999999999905,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1-R2',2020,'E_TRANS',2015,0.1000000000000000055,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1-R2',2025,'E_TRANS',2015,0.1000000000000000055,'$M/PJ','');
INSERT INTO CostVariable VALUES('R1-R2',2030,'E_TRANS',2015,0.1000000000000000055,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2-R1',2020,'E_TRANS',2015,0.1000000000000000055,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2-R1',2025,'E_TRANS',2015,0.1000000000000000055,'$M/PJ','');
INSERT INTO CostVariable VALUES('R2-R1',2030,'E_TRANS',2015,0.1000000000000000055,'$M/PJ','');
CREATE TABLE Demand
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    commodity TEXT
        REFERENCES Commodity (name),
    demand    REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, commodity)
);
INSERT INTO Demand VALUES('R1',2020,'RH',30.0,'','');
INSERT INTO Demand VALUES('R1',2025,'RH',33.0,'','');
INSERT INTO Demand VALUES('R1',2030,'RH',36.0,'','');
INSERT INTO Demand VALUES('R1',2020,'VMT',84.0,'','');
INSERT INTO Demand VALUES('R1',2025,'VMT',91.0,'','');
INSERT INTO Demand VALUES('R1',2030,'VMT',98.0,'','');
INSERT INTO Demand VALUES('R2',2020,'RH',70.0,'','');
INSERT INTO Demand VALUES('R2',2025,'RH',77.0,'','');
INSERT INTO Demand VALUES('R2',2030,'RH',84.0,'','');
INSERT INTO Demand VALUES('R2',2020,'VMT',36.0,'','');
INSERT INTO Demand VALUES('R2',2025,'VMT',39.0,'','');
INSERT INTO Demand VALUES('R2',2030,'VMT',42.0,'','');
CREATE TABLE DemandSpecificDistribution
(
    region      TEXT,
    season      TEXT
        REFERENCES TimeSeason (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES Commodity (name),
    dsd         REAL,
    dsd_notes   TEXT,
    PRIMARY KEY (region, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
INSERT INTO DemandSpecificDistribution VALUES('R1','spring','day','RH',0.05000000000000000277,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','spring','night','RH',0.1000000000000000055,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','summer','day','RH',0.0,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','summer','night','RH',0.0,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','fall','day','RH',0.05000000000000000277,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','fall','night','RH',0.1000000000000000055,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','winter','day','RH',0.2999999999999999889,'');
INSERT INTO DemandSpecificDistribution VALUES('R1','winter','night','RH',0.4000000000000000222,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','spring','day','RH',0.05000000000000000277,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','spring','night','RH',0.1000000000000000055,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','summer','day','RH',0.0,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','summer','night','RH',0.0,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','fall','day','RH',0.05000000000000000277,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','fall','night','RH',0.1000000000000000055,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','winter','day','RH',0.2999999999999999889,'');
INSERT INTO DemandSpecificDistribution VALUES('R2','winter','night','RH',0.4000000000000000222,'');
CREATE TABLE DemandPeriodDistribution
(
    region      TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimeSeason (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES Commodity (name),
    dpd         REAL,
    dpd_notes   TEXT,
    PRIMARY KEY (region, period, season, tod, demand_name),
    CHECK (dpd >= 0 AND dpd <= 1)
);
INSERT INTO DemandPeriodDistribution VALUES('R1',2020,'fall','day','VMT',0.125,'Same as default distribution (segfrac)');
INSERT INTO DemandPeriodDistribution VALUES('R2',2025,'winter','night','VMT',0.125,'Same as default distribution (segfrac)');
CREATE TABLE LoanRate
(
    region  TEXT,
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER
        REFERENCES TimePeriod (period),
    rate    REAL,
    notes   TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE Efficiency
(
    region      TEXT,
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    efficiency  REAL,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
INSERT INTO Efficiency VALUES('R1','ethos','S_IMPETH',2020,'ETH',1.0,'');
INSERT INTO Efficiency VALUES('R1','ethos','S_IMPOIL',2020,'OIL',1.0,'');
INSERT INTO Efficiency VALUES('R1','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO Efficiency VALUES('R1','ethos','S_IMPURN',2020,'URN',1.0,'');
INSERT INTO Efficiency VALUES('R1','OIL','S_OILREF',2020,'GSL',1.0,'');
INSERT INTO Efficiency VALUES('R1','OIL','S_OILREF',2020,'DSL',1.0,'');
INSERT INTO Efficiency VALUES('R1','ETH','T_BLND',2020,'E10',1.0,'');
INSERT INTO Efficiency VALUES('R1','GSL','T_BLND',2020,'E10',1.0,'');
INSERT INTO Efficiency VALUES('R1','NG','E_NGCC',2020,'ELC',0.5500000000000000444,'');
INSERT INTO Efficiency VALUES('R1','NG','E_NGCC',2025,'ELC',0.5500000000000000444,'');
INSERT INTO Efficiency VALUES('R1','NG','E_NGCC',2030,'ELC',0.5500000000000000444,'');
INSERT INTO Efficiency VALUES('R1','SOL','E_SOLPV',2020,'ELC',1.0,'');
INSERT INTO Efficiency VALUES('R1','SOL','E_SOLPV',2025,'ELC',1.0,'');
INSERT INTO Efficiency VALUES('R1','SOL','E_SOLPV',2030,'ELC',1.0,'');
INSERT INTO Efficiency VALUES('R1','URN','E_NUCLEAR',2015,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R1','URN','E_NUCLEAR',2020,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R1','URN','E_NUCLEAR',2025,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R1','URN','E_NUCLEAR',2030,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R1','ELC','E_BATT',2020,'ELC',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R1','ELC','E_BATT',2025,'ELC',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R1','ELC','E_BATT',2030,'ELC',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R1','E10','T_GSL',2020,'VMT',0.25,'');
INSERT INTO Efficiency VALUES('R1','E10','T_GSL',2025,'VMT',0.25,'');
INSERT INTO Efficiency VALUES('R1','E10','T_GSL',2030,'VMT',0.25,'');
INSERT INTO Efficiency VALUES('R1','DSL','T_DSL',2020,'VMT',0.2999999999999999889,'');
INSERT INTO Efficiency VALUES('R1','DSL','T_DSL',2025,'VMT',0.2999999999999999889,'');
INSERT INTO Efficiency VALUES('R1','DSL','T_DSL',2030,'VMT',0.2999999999999999889,'');
INSERT INTO Efficiency VALUES('R1','ELC','T_EV',2020,'VMT',0.8900000000000000133,'');
INSERT INTO Efficiency VALUES('R1','ELC','T_EV',2025,'VMT',0.8900000000000000133,'');
INSERT INTO Efficiency VALUES('R1','ELC','T_EV',2030,'VMT',0.8900000000000000133,'');
INSERT INTO Efficiency VALUES('R1','ELC','R_EH',2020,'RH',1.0,'');
INSERT INTO Efficiency VALUES('R1','ELC','R_EH',2025,'RH',1.0,'');
INSERT INTO Efficiency VALUES('R1','ELC','R_EH',2030,'RH',1.0,'');
INSERT INTO Efficiency VALUES('R1','NG','R_NGH',2020,'RH',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R1','NG','R_NGH',2025,'RH',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R1','NG','R_NGH',2030,'RH',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R2','ethos','S_IMPETH',2020,'ETH',1.0,'');
INSERT INTO Efficiency VALUES('R2','ethos','S_IMPOIL',2020,'OIL',1.0,'');
INSERT INTO Efficiency VALUES('R2','ethos','S_IMPNG',2020,'NG',1.0,'');
INSERT INTO Efficiency VALUES('R2','ethos','S_IMPURN',2020,'URN',1.0,'');
INSERT INTO Efficiency VALUES('R2','OIL','S_OILREF',2020,'GSL',1.0,'');
INSERT INTO Efficiency VALUES('R2','OIL','S_OILREF',2020,'DSL',1.0,'');
INSERT INTO Efficiency VALUES('R2','ETH','T_BLND',2020,'E10',1.0,'');
INSERT INTO Efficiency VALUES('R2','GSL','T_BLND',2020,'E10',1.0,'');
INSERT INTO Efficiency VALUES('R2','NG','E_NGCC',2020,'ELC',0.5500000000000000444,'');
INSERT INTO Efficiency VALUES('R2','NG','E_NGCC',2025,'ELC',0.5500000000000000444,'');
INSERT INTO Efficiency VALUES('R2','NG','E_NGCC',2030,'ELC',0.5500000000000000444,'');
INSERT INTO Efficiency VALUES('R2','SOL','E_SOLPV',2020,'ELC',1.0,'');
INSERT INTO Efficiency VALUES('R2','SOL','E_SOLPV',2025,'ELC',1.0,'');
INSERT INTO Efficiency VALUES('R2','SOL','E_SOLPV',2030,'ELC',1.0,'');
INSERT INTO Efficiency VALUES('R2','URN','E_NUCLEAR',2015,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R2','URN','E_NUCLEAR',2020,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R2','URN','E_NUCLEAR',2025,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R2','URN','E_NUCLEAR',2030,'ELC',0.4000000000000000222,'');
INSERT INTO Efficiency VALUES('R2','ELC','E_BATT',2020,'ELC',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R2','ELC','E_BATT',2025,'ELC',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R2','ELC','E_BATT',2030,'ELC',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R2','E10','T_GSL',2020,'VMT',0.25,'');
INSERT INTO Efficiency VALUES('R2','E10','T_GSL',2025,'VMT',0.25,'');
INSERT INTO Efficiency VALUES('R2','E10','T_GSL',2030,'VMT',0.25,'');
INSERT INTO Efficiency VALUES('R2','DSL','T_DSL',2020,'VMT',0.2999999999999999889,'');
INSERT INTO Efficiency VALUES('R2','DSL','T_DSL',2025,'VMT',0.2999999999999999889,'');
INSERT INTO Efficiency VALUES('R2','DSL','T_DSL',2030,'VMT',0.2999999999999999889,'');
INSERT INTO Efficiency VALUES('R2','ELC','T_EV',2020,'VMT',0.8900000000000000133,'');
INSERT INTO Efficiency VALUES('R2','ELC','T_EV',2025,'VMT',0.8900000000000000133,'');
INSERT INTO Efficiency VALUES('R2','ELC','T_EV',2030,'VMT',0.8900000000000000133,'');
INSERT INTO Efficiency VALUES('R2','ELC','R_EH',2020,'RH',1.0,'');
INSERT INTO Efficiency VALUES('R2','ELC','R_EH',2025,'RH',1.0,'');
INSERT INTO Efficiency VALUES('R2','ELC','R_EH',2030,'RH',1.0,'');
INSERT INTO Efficiency VALUES('R2','NG','R_NGH',2020,'RH',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R2','NG','R_NGH',2025,'RH',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R2','NG','R_NGH',2030,'RH',0.8499999999999999778,'');
INSERT INTO Efficiency VALUES('R1-R2','ELC','E_TRANS',2015,'ELC',0.9000000000000000222,'');
INSERT INTO Efficiency VALUES('R2-R1','ELC','E_TRANS',2015,'ELC',0.9000000000000000222,'');
CREATE TABLE EmissionActivity
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES Commodity (name),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    activity    REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm, input_comm, tech, vintage, output_comm)
);
INSERT INTO EmissionActivity VALUES('R1','CO2','ethos','S_IMPNG',2020,'NG',50.29999999999999716,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO EmissionActivity VALUES('R1','CO2','OIL','S_OILREF',2020,'GSL',67.20000000000000284,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO EmissionActivity VALUES('R1','CO2','OIL','S_OILREF',2020,'DSL',69.40000000000000569,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO EmissionActivity VALUES('R2','CO2','ethos','S_IMPNG',2020,'NG',50.29999999999999716,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO EmissionActivity VALUES('R2','CO2','OIL','S_OILREF',2020,'GSL',67.20000000000000284,'kT/PJ','taken from MIT Energy Fact Sheet');
INSERT INTO EmissionActivity VALUES('R2','CO2','OIL','S_OILREF',2020,'DSL',69.40000000000000569,'kT/PJ','taken from MIT Energy Fact Sheet');
CREATE TABLE ExistingCapacity
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    units    TEXT,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
INSERT INTO ExistingCapacity VALUES('R1','E_NUCLEAR',2015,0.07000000000000000667,'GW','');
INSERT INTO ExistingCapacity VALUES('R2','E_NUCLEAR',2015,0.02999999999999999889,'GW','');
INSERT INTO ExistingCapacity VALUES('R1-R2','E_TRANS',2015,10.0,'GW','');
INSERT INTO ExistingCapacity VALUES('R2-R1','E_TRANS',2015,10.0,'GW','');
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
);
CREATE TABLE GrowthRateMax
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE GrowthRateSeed
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    seed   REAL,
    units  TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE LoanLifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LoanLifetimeTech VALUES('R1','S_IMPETH',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','S_IMPOIL',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','S_IMPNG',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','S_IMPURN',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','S_OILREF',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','E_NGCC',30.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','E_SOLPV',30.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','E_BATT',20.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','E_NUCLEAR',50.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','T_BLND',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','T_DSL',12.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','T_GSL',12.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','T_EV',12.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','R_EH',20.0,'');
INSERT INTO LoanLifetimeTech VALUES('R1','R_NGH',20.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','S_IMPETH',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','S_IMPOIL',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','S_IMPNG',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','S_IMPURN',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','S_OILREF',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','E_NGCC',30.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','E_SOLPV',30.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','E_BATT',20.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','E_NUCLEAR',50.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','T_BLND',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','T_DSL',12.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','T_GSL',12.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','T_EV',12.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','R_EH',20.0,'');
INSERT INTO LoanLifetimeTech VALUES('R2','R_NGH',20.0,'');
CREATE TABLE LifetimeProcess
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech, vintage)
);
CREATE TABLE LifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LifetimeTech VALUES('R1','S_IMPETH',100.0,'');
INSERT INTO LifetimeTech VALUES('R1','S_IMPOIL',100.0,'');
INSERT INTO LifetimeTech VALUES('R1','S_IMPNG',100.0,'');
INSERT INTO LifetimeTech VALUES('R1','S_IMPURN',100.0,'');
INSERT INTO LifetimeTech VALUES('R1','S_OILREF',100.0,'');
INSERT INTO LifetimeTech VALUES('R1','E_NGCC',30.0,'');
INSERT INTO LifetimeTech VALUES('R1','E_SOLPV',30.0,'');
INSERT INTO LifetimeTech VALUES('R1','E_BATT',20.0,'');
INSERT INTO LifetimeTech VALUES('R1','E_NUCLEAR',50.0,'');
INSERT INTO LifetimeTech VALUES('R1','T_BLND',100.0,'');
INSERT INTO LifetimeTech VALUES('R1','T_DSL',12.0,'');
INSERT INTO LifetimeTech VALUES('R1','T_GSL',12.0,'');
INSERT INTO LifetimeTech VALUES('R1','T_EV',12.0,'');
INSERT INTO LifetimeTech VALUES('R1','R_EH',20.0,'');
INSERT INTO LifetimeTech VALUES('R1','R_NGH',20.0,'');
INSERT INTO LifetimeTech VALUES('R2','S_IMPETH',100.0,'');
INSERT INTO LifetimeTech VALUES('R2','S_IMPOIL',100.0,'');
INSERT INTO LifetimeTech VALUES('R2','S_IMPNG',100.0,'');
INSERT INTO LifetimeTech VALUES('R2','S_IMPURN',100.0,'');
INSERT INTO LifetimeTech VALUES('R2','S_OILREF',100.0,'');
INSERT INTO LifetimeTech VALUES('R2','E_NGCC',30.0,'');
INSERT INTO LifetimeTech VALUES('R2','E_SOLPV',30.0,'');
INSERT INTO LifetimeTech VALUES('R2','E_BATT',20.0,'');
INSERT INTO LifetimeTech VALUES('R2','E_NUCLEAR',50.0,'');
INSERT INTO LifetimeTech VALUES('R2','T_BLND',100.0,'');
INSERT INTO LifetimeTech VALUES('R2','T_DSL',12.0,'');
INSERT INTO LifetimeTech VALUES('R2','T_GSL',12.0,'');
INSERT INTO LifetimeTech VALUES('R2','T_EV',12.0,'');
INSERT INTO LifetimeTech VALUES('R2','R_EH',20.0,'');
INSERT INTO LifetimeTech VALUES('R2','R_NGH',20.0,'');
INSERT INTO LifetimeTech VALUES('R1-R2','E_TRANS',30.0,'');
INSERT INTO LifetimeTech VALUES('R2-R1','E_TRANS',30.0,'');
CREATE TABLE LinkedTech
(
    primary_region TEXT,
    primary_tech   TEXT
        REFERENCES Technology (tech),
    emis_comm      TEXT
        REFERENCES Commodity (name),
    driven_tech    TEXT
        REFERENCES Technology (tech),
    notes          TEXT,
    PRIMARY KEY (primary_region, primary_tech, emis_comm)
);
CREATE TABLE MaxActivity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    max_act REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MaxCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    max_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MaxResource
(
    region  TEXT,
    tech    TEXT
        REFERENCES Technology (tech),
    max_res REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE MinActivity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    min_act REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
INSERT INTO MinActivity VALUES('R1',2020,'T_GSL',35.0,'','');
INSERT INTO MinActivity VALUES('R1',2025,'T_GSL',35.0,'','');
INSERT INTO MinActivity VALUES('R1',2030,'T_GSL',35.0,'','');
INSERT INTO MinActivity VALUES('R2',2020,'T_GSL',15.0,'','');
INSERT INTO MinActivity VALUES('R2',2025,'T_GSL',15.0,'','');
INSERT INTO MinActivity VALUES('R2',2030,'T_GSL',15.0,'','');
CREATE TABLE MaxCapacityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    max_cap    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE MinCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    min_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MinCapacityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    min_cap    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE OutputCurtailment
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimePeriod (period),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    curtailment REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE OutputNetCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    period   INTEGER
        REFERENCES TimePeriod (period),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE OutputBuiltCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, tech, vintage)
);
CREATE TABLE OutputRetiredCapacity
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT
        REFERENCES SectorLabel (sector),
    period   INTEGER
        REFERENCES TimePeriod (period),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    capacity REAL,
    PRIMARY KEY (region, scenario, period, tech, vintage)
);
CREATE TABLE OutputFlowIn
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimeSeason (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE OutputFlowOut
(
    scenario    TEXT,
    region      TEXT,
    sector      TEXT
        REFERENCES SectorLabel (sector),
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimePeriod (period),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    input_comm  TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm TEXT
        REFERENCES Commodity (name),
    flow        REAL,
    PRIMARY KEY (region, scenario, period, season, tod, input_comm, tech, vintage, output_comm)
);
CREATE TABLE PlanningReserveMargin
(
    region TEXT
        PRIMARY KEY
        REFERENCES Region (region),
    margin REAL
);
CREATE TABLE RampDown
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    PRIMARY KEY (region, tech)
);
CREATE TABLE RampUp
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    rate   REAL,
    PRIMARY KEY (region, tech)
);
CREATE TABLE Region
(
    region TEXT
        PRIMARY KEY,
    notes  TEXT
);
INSERT INTO Region VALUES('R1',NULL);
INSERT INTO Region VALUES('R2',NULL);
CREATE TABLE TimeSegmentFraction
(
    season  TEXT
        REFERENCES TimeSeason (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    segfrac REAL,
    notes   TEXT,
    PRIMARY KEY (season, tod),
    CHECK (segfrac >= 0 AND segfrac <= 1)
);
INSERT INTO TimeSegmentFraction VALUES('spring','day',0.125,'Spring - Day');
INSERT INTO TimeSegmentFraction VALUES('spring','night',0.125,'Spring - Night');
INSERT INTO TimeSegmentFraction VALUES('summer','day',0.125,'Summer - Day');
INSERT INTO TimeSegmentFraction VALUES('summer','night',0.125,'Summer - Night');
INSERT INTO TimeSegmentFraction VALUES('fall','day',0.125,'Fall - Day');
INSERT INTO TimeSegmentFraction VALUES('fall','night',0.125,'Fall - Night');
INSERT INTO TimeSegmentFraction VALUES('winter','day',0.125,'Winter - Day');
INSERT INTO TimeSegmentFraction VALUES('winter','night',0.125,'Winter - Night');
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO StorageDuration VALUES('R1','E_BATT',8.0,'8-hour duration specified as fraction of a day');
INSERT INTO StorageDuration VALUES('R2','E_BATT',8.0,'8-hour duration specified as fraction of a day');
CREATE TABLE StorageFraction
(   
    region TEXT,
    period INTEGER REFERENCES TimePeriod (period),
    season TEXT REFERENCES TimeSeason (season),
    tod TEXT REFERENCES TimeOfDay (tod),
    tech TEXT REFERENCES Technology (tech),
    vintage INTEGER REFERENCES TimePeriod (period),
    frac REAL,
    notes TEXT
);
INSERT INTO StorageFraction VALUES('R1',2025,'winter','day','E_BATT',2025,0.5,'');
INSERT INTO StorageFraction VALUES('R2',2020,'summer','day','E_BATT',2020,0.5,'');
CREATE TABLE TechnologyType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TechnologyType VALUES('r','resource technology');
INSERT INTO TechnologyType VALUES('p','production technology');
INSERT INTO TechnologyType VALUES('pb','baseload production technology');
INSERT INTO TechnologyType VALUES('ps','storage production technology');
CREATE TABLE MinTechInputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech)
);
INSERT INTO MinTechInputSplit VALUES('R1',2020,'GSL','T_BLND',0.9000000000000000222,'');
INSERT INTO MinTechInputSplit VALUES('R1',2020,'ETH','T_BLND',0.1000000000000000055,'');
INSERT INTO MinTechInputSplit VALUES('R1',2025,'GSL','T_BLND',0.9000000000000000222,'');
INSERT INTO MinTechInputSplit VALUES('R1',2025,'ETH','T_BLND',0.1000000000000000055,'');
INSERT INTO MinTechInputSplit VALUES('R1',2030,'GSL','T_BLND',0.9000000000000000222,'');
INSERT INTO MinTechInputSplit VALUES('R1',2030,'ETH','T_BLND',0.1000000000000000055,'');
INSERT INTO MinTechInputSplit VALUES('R2',2020,'GSL','T_BLND',0.7199999999999999734,'');
INSERT INTO MinTechInputSplit VALUES('R2',2020,'ETH','T_BLND',0.08000000000000000166,'');
INSERT INTO MinTechInputSplit VALUES('R2',2025,'GSL','T_BLND',0.7199999999999999734,'');
INSERT INTO MinTechInputSplit VALUES('R2',2025,'ETH','T_BLND',0.08000000000000000166,'');
INSERT INTO MinTechInputSplit VALUES('R2',2030,'GSL','T_BLND',0.7199999999999999734,'');
INSERT INTO MinTechInputSplit VALUES('R2',2030,'ETH','T_BLND',0.08000000000000000166,'');
CREATE TABLE MinTechInputSplitAnnual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech)
);
CREATE TABLE MinTechOutputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm)
);
INSERT INTO MinTechOutputSplit VALUES('R1',2020,'S_OILREF','GSL',0.9000000000000000222,'');
INSERT INTO MinTechOutputSplit VALUES('R1',2020,'S_OILREF','DSL',0.1000000000000000055,'');
INSERT INTO MinTechOutputSplit VALUES('R1',2025,'S_OILREF','GSL',0.9000000000000000222,'');
INSERT INTO MinTechOutputSplit VALUES('R1',2025,'S_OILREF','DSL',0.1000000000000000055,'');
INSERT INTO MinTechOutputSplit VALUES('R1',2030,'S_OILREF','GSL',0.9000000000000000222,'');
INSERT INTO MinTechOutputSplit VALUES('R1',2030,'S_OILREF','DSL',0.1000000000000000055,'');
INSERT INTO MinTechOutputSplit VALUES('R2',2020,'S_OILREF','GSL',0.7199999999999999734,'');
INSERT INTO MinTechOutputSplit VALUES('R2',2020,'S_OILREF','DSL',0.08000000000000000166,'');
INSERT INTO MinTechOutputSplit VALUES('R2',2025,'S_OILREF','GSL',0.7199999999999999734,'');
INSERT INTO MinTechOutputSplit VALUES('R2',2025,'S_OILREF','DSL',0.08000000000000000166,'');
INSERT INTO MinTechOutputSplit VALUES('R2',2030,'S_OILREF','GSL',0.7199999999999999734,'');
INSERT INTO MinTechOutputSplit VALUES('R2',2030,'S_OILREF','DSL',0.08000000000000000166,'');
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(1,'day');
INSERT INTO TimeOfDay VALUES(2,'night');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(1,2015,'e');
INSERT INTO TimePeriod VALUES(2,2020,'f');
INSERT INTO TimePeriod VALUES(3,2025,'f');
INSERT INTO TimePeriod VALUES(4,2030,'f');
INSERT INTO TimePeriod VALUES(5,2035,'f');
CREATE TABLE TimeSeason
(
    sequence INTEGER UNIQUE,
    season   TEXT
        PRIMARY KEY
);
INSERT INTO TimeSeason VALUES(1,'spring');
INSERT INTO TimeSeason VALUES(2,'summer');
INSERT INTO TimeSeason VALUES(3,'fall');
INSERT INTO TimeSeason VALUES(4,'winter');
CREATE TABLE TimePeriodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TimePeriodType VALUES('e','existing vintages');
INSERT INTO TimePeriodType VALUES('f','future');
CREATE TABLE MaxActivityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MaxCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MaxAnnualCapacityFactor
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    tech        TEXT
        REFERENCES Technology (tech),
    output_comm TEXT
        REFERENCES Commodity (name),
    factor      REAL,
    source      TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE MaxNewCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    max_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MaxNewCapacityGroup
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    group_name  TEXT
        REFERENCES TechGroup (group_name),
    max_new_cap REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE MaxNewCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinActivityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinAnnualCapacityFactor
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    tech        TEXT
        REFERENCES Technology (tech),
    output_comm TEXT
        REFERENCES Commodity (name),
    factor      REAL,
    source      TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE MinCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    min_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE MinNewCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech    TEXT
        REFERENCES Technology (tech),
    min_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech)
);
CREATE TABLE MinNewCapacityGroup
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    group_name  TEXT
        REFERENCES TechGroup (group_name),
    min_new_cap REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE MinNewCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    group_name     TEXT
        REFERENCES TechGroup (group_name),
    max_proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, group_name)
);
CREATE TABLE OutputEmission
(
    scenario  TEXT,
    region    TEXT,
    sector    TEXT
        REFERENCES SectorLabel (sector),
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT
        REFERENCES Commodity (name),
    tech      TEXT
        REFERENCES Technology (tech),
    vintage   INTEGER
        REFERENCES TimePeriod (period),
    emission  REAL,
    PRIMARY KEY (region, scenario, period, emis_comm, tech, vintage)
);
CREATE TABLE MinActivityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    min_act    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE EmissionLimit
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT
        REFERENCES Commodity (name),
    value     REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm)
);
INSERT INTO EmissionLimit VALUES('R1',2020,'CO2',25000.0,'kT CO2','');
INSERT INTO EmissionLimit VALUES('R1',2025,'CO2',24000.0,'kT CO2','');
INSERT INTO EmissionLimit VALUES('R1',2030,'CO2',23000.0,'kT CO2','');
INSERT INTO EmissionLimit VALUES('global',2020,'CO2',37500.0,'kT CO2','');
INSERT INTO EmissionLimit VALUES('global',2025,'CO2',36000.0,'kT CO2','');
INSERT INTO EmissionLimit VALUES('global',2030,'CO2',34500.0,'kT CO2','');
CREATE TABLE MaxActivityGroup
(
    region     TEXT,
    period     INTEGER
        REFERENCES TimePeriod (period),
    group_name TEXT
        REFERENCES TechGroup (group_name),
    max_act    REAL,
    units      TEXT,
    notes      TEXT,
    PRIMARY KEY (region, period, group_name)
);
CREATE TABLE RPSRequirement
(
    region      TEXT    NOT NULL
        REFERENCES Region (region),
    period      INTEGER NOT NULL
        REFERENCES TimePeriod (period),
    tech_group  TEXT    NOT NULL
        REFERENCES TechGroup (group_name),
    requirement REAL    NOT NULL,
    notes       TEXT
);
CREATE TABLE TechGroupMember
(
    group_name TEXT
        REFERENCES TechGroup (group_name),
    tech       TEXT
        REFERENCES Technology (tech),
    PRIMARY KEY (group_name, tech)
);
CREATE TABLE Technology
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
    variable     INTEGER NOT NULL DEFAULT 0,
    exchange     INTEGER NOT NULL DEFAULT 0,
    description  TEXT,
    FOREIGN KEY (flag) REFERENCES TechnologyType (label)
);
INSERT INTO Technology VALUES('S_IMPETH','r','supply','','',1,0,0,0,0,0,0,0,' imported ethanol');
INSERT INTO Technology VALUES('S_IMPOIL','r','supply','','',1,0,0,0,0,0,0,0,' imported crude oil');
INSERT INTO Technology VALUES('S_IMPNG','r','supply','','',1,0,0,0,0,0,0,0,' imported natural gas');
INSERT INTO Technology VALUES('S_IMPURN','r','supply','','',1,0,0,0,0,0,0,0,' imported uranium');
INSERT INTO Technology VALUES('S_OILREF','p','supply','','',0,0,0,1,0,0,0,0,' crude oil refinery');
INSERT INTO Technology VALUES('E_NGCC','p','electric','','',0,0,0,0,0,0,0,0,' natural gas combined-cycle');
INSERT INTO Technology VALUES('E_SOLPV','p','electric','','',0,0,0,0,0,0,0,0,' solar photovoltaic');
INSERT INTO Technology VALUES('E_BATT','ps','electric','','',0,0,0,0,0,0,0,0,' lithium-ion battery');
INSERT INTO Technology VALUES('E_NUCLEAR','pb','electric','','',0,0,0,0,0,0,0,0,' nuclear power plant');
INSERT INTO Technology VALUES('T_BLND','p','transport','','',0,0,0,0,0,0,0,0,'ethanol - gasoline blending process');
INSERT INTO Technology VALUES('T_DSL','p','transport','','',0,0,0,0,0,0,0,0,'diesel vehicle');
INSERT INTO Technology VALUES('T_GSL','p','transport','','',0,0,0,0,0,0,0,0,'gasoline vehicle');
INSERT INTO Technology VALUES('T_EV','p','transport','','',0,0,0,0,0,0,0,0,'electric vehicle');
INSERT INTO Technology VALUES('R_EH','p','residential','','',0,0,0,0,0,0,0,0,' electric residential heating');
INSERT INTO Technology VALUES('R_NGH','p','residential','','',0,0,0,0,0,0,0,0,' natural gas residential heating');
INSERT INTO Technology VALUES('E_TRANS','p','electric','','',0,0,0,0,0,0,0,1,'electric transmission');
CREATE TABLE OutputCost
(
    scenario TEXT,
    region   TEXT,
    period   INTEGER,
    tech     TEXT,
    vintage  INTEGER,
    d_invest REAL,
    d_fixed  REAL,
    d_var    REAL,
    d_emiss  REAL,
    invest   REAL,
    fixed    REAL,
    var      REAL,
    emiss    REAL,
    PRIMARY KEY (scenario, region, period, tech, vintage),
    FOREIGN KEY (vintage) REFERENCES TimePeriod (period),
    FOREIGN KEY (tech) REFERENCES Technology (tech)
);
COMMIT;
