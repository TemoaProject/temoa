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
    season  TEXT
        REFERENCES TimeSeason (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    tech    TEXT
        REFERENCES Technology (tech),
    vintage INTEGER,
    factor  REAL,
    notes   TEXT,
    PRIMARY KEY (region, season, tod, tech, vintage),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO CapacityFactorProcess VALUES('utopia','inter','day','E31',2000,0.2752999999999999892,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','inter','night','E31',2000,0.2752999999999999892,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','winter','day','E31',2000,0.2752999999999999892,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','winter','night','E31',2000,0.2752999999999999892,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','summer','day','E31',2000,0.2752999999999999892,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','summer','night','E31',2000,0.2752999999999999892,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','inter','day','E31',2010,0.2756000000000000116,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','inter','night','E31',2010,0.2756000000000000116,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','winter','day','E31',2010,0.2756000000000000116,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','winter','night','E31',2010,0.2756000000000000116,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','summer','day','E31',2010,0.2756000000000000116,'');
INSERT INTO CapacityFactorProcess VALUES('utopia','summer','night','E31',2010,0.2756000000000000116,'');
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
INSERT INTO CapacityFactorTech VALUES('utopia','inter','day','E01',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','night','E01',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','day','E01',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','night','E01',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','day','E01',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','night','E01',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','day','E21',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','night','E21',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','day','E21',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','night','E21',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','day','E21',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','night','E21',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','day','E31',0.2750000000000000222,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','night','E31',0.2750000000000000222,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','day','E31',0.2750000000000000222,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','night','E31',0.2750000000000000222,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','day','E31',0.2750000000000000222,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','night','E31',0.2750000000000000222,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','day','E51',0.1700000000000000122,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','night','E51',0.1700000000000000122,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','day','E51',0.1700000000000000122,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','night','E51',0.1700000000000000122,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','day','E51',0.1700000000000000122,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','night','E51',0.1700000000000000122,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','day','E70',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','inter','night','E70',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','day','E70',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','winter','night','E70',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','day','E70',0.8000000000000000444,'');
INSERT INTO CapacityFactorTech VALUES('utopia','summer','night','E70',0.8000000000000000444,'');
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('utopia','E01',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('utopia','E21',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('utopia','E31',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('utopia','E51',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('utopia','E70',31.53999999999999915,'');
INSERT INTO CapacityToActivity VALUES('utopia','RHE',1.0,'');
INSERT INTO CapacityToActivity VALUES('utopia','RHO',1.0,'');
INSERT INTO CapacityToActivity VALUES('utopia','RL1',1.0,'');
INSERT INTO CapacityToActivity VALUES('utopia','SRE',1.0,'');
INSERT INTO CapacityToActivity VALUES('utopia','TXD',1.0,'');
INSERT INTO CapacityToActivity VALUES('utopia','TXE',1.0,'');
INSERT INTO CapacityToActivity VALUES('utopia','TXG',1.0,'');
CREATE TABLE Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
INSERT INTO Commodity VALUES('ethos','s','# dummy commodity to supply inputs (makes graph easier to read)');
INSERT INTO Commodity VALUES('DSL','p','# diesel');
INSERT INTO Commodity VALUES('ELC','p','# electricity');
INSERT INTO Commodity VALUES('FEQ','p','# fossil equivalent');
INSERT INTO Commodity VALUES('GSL','p','# gasoline');
INSERT INTO Commodity VALUES('HCO','p','# coal');
INSERT INTO Commodity VALUES('HYD','p','# water');
INSERT INTO Commodity VALUES('OIL','p','# crude oil');
INSERT INTO Commodity VALUES('URN','p','# uranium');
INSERT INTO Commodity VALUES('co2','e','#CO2 emissions');
INSERT INTO Commodity VALUES('nox','e','#NOX emissions');
INSERT INTO Commodity VALUES('RH','d','# residential heating');
INSERT INTO Commodity VALUES('RL','d','# residential lighting');
INSERT INTO Commodity VALUES('TX','d','# transportation');
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
INSERT INTO CostFixed VALUES('utopia',1990,'E01',1960,40.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E01',1970,40.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E01',1980,40.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E01',1990,40.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E01',1970,70.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E01',1980,70.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E01',1990,70.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E01',2000,70.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E01',1980,100.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E01',1990,100.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E01',2000,100.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E01',2010,100.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E21',1990,500.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E21',1990,500.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E21',1990,500.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E21',2000,500.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E21',2000,500.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E21',2010,500.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E31',1980,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E31',1990,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E31',1980,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E31',1990,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E31',2000,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E31',1980,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E31',1990,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E31',2000,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E31',2010,75.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E51',1980,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E51',1990,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E51',1980,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E51',1990,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E51',2000,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E51',1980,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E51',1990,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E51',2000,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E51',2010,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E70',1960,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E70',1970,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E70',1980,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'E70',1990,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E70',1970,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E70',1980,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E70',1990,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'E70',2000,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E70',1980,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E70',1990,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E70',2000,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'E70',2010,30.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'RHO',1970,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'RHO',1980,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'RHO',1990,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'RHO',1980,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'RHO',1990,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'RHO',2000,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'RHO',1990,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'RHO',2000,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'RHO',2010,1.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'RL1',1980,9.46000000000000086,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'RL1',1990,9.46000000000000086,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'RL1',2000,9.46000000000000086,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'RL1',2010,9.46000000000000086,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXD',1970,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXD',1980,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXD',1990,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXD',1980,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXD',1990,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXD',2000,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'TXD',2000,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'TXD',2010,52.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXE',1990,100.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXE',1990,90.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXE',2000,90.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'TXE',2000,80.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'TXE',2010,80.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXG',1970,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXG',1980,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',1990,'TXG',1990,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXG',1980,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXG',1990,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',2000,'TXG',2000,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'TXG',2000,48.0,'','');
INSERT INTO CostFixed VALUES('utopia',2010,'TXG',2010,48.0,'','');
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
INSERT INTO CostInvest VALUES('utopia','E01',1990,2000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E01',2000,1300.0,'','');
INSERT INTO CostInvest VALUES('utopia','E01',2010,1200.0,'','');
INSERT INTO CostInvest VALUES('utopia','E21',1990,5000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E21',2000,5000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E21',2010,5000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E31',1990,3000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E31',2000,3000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E31',2010,3000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E51',1990,900.0,'','');
INSERT INTO CostInvest VALUES('utopia','E51',2000,900.0,'','');
INSERT INTO CostInvest VALUES('utopia','E51',2010,900.0,'','');
INSERT INTO CostInvest VALUES('utopia','E70',1990,1000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E70',2000,1000.0,'','');
INSERT INTO CostInvest VALUES('utopia','E70',2010,1000.0,'','');
INSERT INTO CostInvest VALUES('utopia','RHE',1990,90.0,'','');
INSERT INTO CostInvest VALUES('utopia','RHE',2000,90.0,'','');
INSERT INTO CostInvest VALUES('utopia','RHE',2010,90.0,'','');
INSERT INTO CostInvest VALUES('utopia','RHO',1990,100.0,'','');
INSERT INTO CostInvest VALUES('utopia','RHO',2000,100.0,'','');
INSERT INTO CostInvest VALUES('utopia','RHO',2010,100.0,'','');
INSERT INTO CostInvest VALUES('utopia','SRE',1990,100.0,'','');
INSERT INTO CostInvest VALUES('utopia','SRE',2000,100.0,'','');
INSERT INTO CostInvest VALUES('utopia','SRE',2010,100.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXD',1990,1044.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXD',2000,1044.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXD',2010,1044.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXE',1990,2000.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXE',2000,1750.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXE',2010,1500.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXG',1990,1044.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXG',2000,1044.0,'','');
INSERT INTO CostInvest VALUES('utopia','TXG',2010,1044.0,'','');
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
INSERT INTO CostVariable VALUES('utopia',1990,'IMPDSL1',1990,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'IMPDSL1',1990,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'IMPDSL1',1990,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'IMPGSL1',1990,15.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'IMPGSL1',1990,15.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'IMPGSL1',1990,15.0,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'IMPHCO1',1990,2.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'IMPHCO1',1990,2.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'IMPHCO1',1990,2.0,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'IMPOIL1',1990,8.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'IMPOIL1',1990,8.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'IMPOIL1',1990,8.0,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'IMPURN1',1990,2.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'IMPURN1',1990,2.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'IMPURN1',1990,2.0,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E01',1960,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E01',1970,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E01',1980,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E01',1990,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E01',1970,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E01',1980,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E01',1990,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E01',2000,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E01',1980,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E01',1990,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E01',2000,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E01',2010,0.2999999999999999889,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E21',1990,1.5,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E21',1990,1.5,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E21',1990,1.5,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E21',2000,1.5,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E21',2000,1.5,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E21',2010,1.5,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E70',1960,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E70',1970,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E70',1980,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'E70',1990,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E70',1970,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E70',1980,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E70',1990,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'E70',2000,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E70',1980,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E70',1990,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E70',2000,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'E70',2010,0.4000000000000000222,'','');
INSERT INTO CostVariable VALUES('utopia',1990,'SRE',1990,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'SRE',1990,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2000,'SRE',2000,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'SRE',1990,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'SRE',2000,10.0,'','');
INSERT INTO CostVariable VALUES('utopia',2010,'SRE',2010,10.0,'','');
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
INSERT INTO Demand VALUES('utopia',1990,'RH',25.19999999999999929,'','');
INSERT INTO Demand VALUES('utopia',2000,'RH',37.79999999999999715,'','');
INSERT INTO Demand VALUES('utopia',2010,'RH',56.70000000000000284,'','');
INSERT INTO Demand VALUES('utopia',1990,'RL',5.599999999999999645,'','');
INSERT INTO Demand VALUES('utopia',2000,'RL',8.400000000000000355,'','');
INSERT INTO Demand VALUES('utopia',2010,'RL',12.59999999999999965,'','');
INSERT INTO Demand VALUES('utopia',1990,'TX',5.200000000000000177,'','');
INSERT INTO Demand VALUES('utopia',2000,'TX',7.799999999999999823,'','');
INSERT INTO Demand VALUES('utopia',2010,'TX',11.68999999999999951,'','');
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
INSERT INTO DemandSpecificDistribution VALUES('utopia','inter','day','RH',0.1199999999999999956,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','inter','night','RH',0.05999999999999999778,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','winter','day','RH',0.5466999999999999638,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','winter','night','RH',0.2732999999999999874,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','inter','day','RL',0.1499999999999999945,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','inter','night','RL',0.05000000000000000277,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','summer','day','RL',0.1499999999999999945,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','summer','night','RL',0.05000000000000000277,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','winter','day','RL',0.5,'');
INSERT INTO DemandSpecificDistribution VALUES('utopia','winter','night','RL',0.1000000000000000055,'');
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
INSERT INTO Efficiency VALUES('utopia','ethos','IMPDSL1',1990,'DSL',1.0,'');
INSERT INTO Efficiency VALUES('utopia','ethos','IMPGSL1',1990,'GSL',1.0,'');
INSERT INTO Efficiency VALUES('utopia','ethos','IMPHCO1',1990,'HCO',1.0,'');
INSERT INTO Efficiency VALUES('utopia','ethos','IMPOIL1',1990,'OIL',1.0,'');
INSERT INTO Efficiency VALUES('utopia','ethos','IMPURN1',1990,'URN',1.0,'');
INSERT INTO Efficiency VALUES('utopia','ethos','IMPFEQ',1990,'FEQ',1.0,'');
INSERT INTO Efficiency VALUES('utopia','ethos','IMPHYD',1990,'HYD',1.0,'');
INSERT INTO Efficiency VALUES('utopia','HCO','E01',1960,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HCO','E01',1970,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HCO','E01',1980,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HCO','E01',1990,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HCO','E01',2000,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HCO','E01',2010,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','FEQ','E21',1990,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','FEQ','E21',2000,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','FEQ','E21',2010,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','URN','E21',1990,'ELC',0.4000000000000000222,'# 1/2.5');
INSERT INTO Efficiency VALUES('utopia','URN','E21',2000,'ELC',0.4000000000000000222,'# 1/2.5');
INSERT INTO Efficiency VALUES('utopia','URN','E21',2010,'ELC',0.4000000000000000222,'# 1/2.5');
INSERT INTO Efficiency VALUES('utopia','HYD','E31',1980,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HYD','E31',1990,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HYD','E31',2000,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','HYD','E31',2010,'ELC',0.3200000000000000066,'# 1/3.125');
INSERT INTO Efficiency VALUES('utopia','DSL','E70',1960,'ELC',0.2939999999999999836,'# 1/3.4');
INSERT INTO Efficiency VALUES('utopia','DSL','E70',1970,'ELC',0.2939999999999999836,'# 1/3.4');
INSERT INTO Efficiency VALUES('utopia','DSL','E70',1980,'ELC',0.2939999999999999836,'# 1/3.4');
INSERT INTO Efficiency VALUES('utopia','DSL','E70',1990,'ELC',0.2939999999999999836,'# 1/3.4');
INSERT INTO Efficiency VALUES('utopia','DSL','E70',2000,'ELC',0.2939999999999999836,'# 1/3.4');
INSERT INTO Efficiency VALUES('utopia','DSL','E70',2010,'ELC',0.2939999999999999836,'# 1/3.4');
INSERT INTO Efficiency VALUES('utopia','ELC','E51',1980,'ELC',0.7199999999999999734,'# 1/1.3889');
INSERT INTO Efficiency VALUES('utopia','ELC','E51',1990,'ELC',0.7199999999999999734,'# 1/1.3889');
INSERT INTO Efficiency VALUES('utopia','ELC','E51',2000,'ELC',0.7199999999999999734,'# 1/1.3889');
INSERT INTO Efficiency VALUES('utopia','ELC','E51',2010,'ELC',0.7199999999999999734,'# 1/1.3889');
INSERT INTO Efficiency VALUES('utopia','ELC','RHE',1990,'RH',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','RHE',2000,'RH',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','RHE',2010,'RH',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','RHO',1970,'RH',0.6999999999999999556,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','RHO',1980,'RH',0.6999999999999999556,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','RHO',1990,'RH',0.6999999999999999556,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','RHO',2000,'RH',0.6999999999999999556,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','RHO',2010,'RH',0.6999999999999999556,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','RL1',1980,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','RL1',1990,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','RL1',2000,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','RL1',2010,'RL',1.0,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','OIL','SRE',1990,'DSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO Efficiency VALUES('utopia','OIL','SRE',2000,'DSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO Efficiency VALUES('utopia','OIL','SRE',2010,'DSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO Efficiency VALUES('utopia','OIL','SRE',1990,'GSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO Efficiency VALUES('utopia','OIL','SRE',2000,'GSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO Efficiency VALUES('utopia','OIL','SRE',2010,'GSL',1.0,'# direct translation from PRC_INP2, PRC_OUT');
INSERT INTO Efficiency VALUES('utopia','DSL','TXD',1970,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','TXD',1980,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','TXD',1990,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','TXD',2000,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','DSL','TXD',2010,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','TXE',1990,'TX',0.8269999999999999574,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','TXE',2000,'TX',0.8269999999999999574,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','ELC','TXE',2010,'TX',0.8269999999999999574,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','GSL','TXG',1970,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','GSL','TXG',1980,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','GSL','TXG',1990,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','GSL','TXG',2000,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
INSERT INTO Efficiency VALUES('utopia','GSL','TXG',2010,'TX',0.2310000000000000108,'# direct translation from DMD_EFF');
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
INSERT INTO EmissionActivity VALUES('utopia','co2','ethos','IMPDSL1',1990,'DSL',0.07499999999999999723,'','');
INSERT INTO EmissionActivity VALUES('utopia','co2','ethos','IMPGSL1',1990,'GSL',0.07499999999999999723,'','');
INSERT INTO EmissionActivity VALUES('utopia','co2','ethos','IMPHCO1',1990,'HCO',0.08899999999999999579,'','');
INSERT INTO EmissionActivity VALUES('utopia','co2','ethos','IMPOIL1',1990,'OIL',0.07499999999999999723,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','DSL','TXD',1970,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','DSL','TXD',1980,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','DSL','TXD',1990,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','DSL','TXD',2000,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','DSL','TXD',2010,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','GSL','TXG',1970,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','GSL','TXG',1980,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','GSL','TXG',1990,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','GSL','TXG',2000,'TX',1.0,'','');
INSERT INTO EmissionActivity VALUES('utopia','nox','GSL','TXG',2010,'TX',1.0,'','');
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
INSERT INTO ExistingCapacity VALUES('utopia','E01',1960,0.1749999999999999889,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E01',1970,0.1749999999999999889,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E01',1980,0.1499999999999999945,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E31',1980,0.1000000000000000055,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E51',1980,0.5,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E70',1960,0.05000000000000000277,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E70',1970,0.05000000000000000277,'','');
INSERT INTO ExistingCapacity VALUES('utopia','E70',1980,0.2000000000000000111,'','');
INSERT INTO ExistingCapacity VALUES('utopia','RHO',1970,12.5,'','');
INSERT INTO ExistingCapacity VALUES('utopia','RHO',1980,12.5,'','');
INSERT INTO ExistingCapacity VALUES('utopia','RL1',1980,5.599999999999999645,'','');
INSERT INTO ExistingCapacity VALUES('utopia','TXD',1970,0.4000000000000000222,'','');
INSERT INTO ExistingCapacity VALUES('utopia','TXD',1980,0.2000000000000000111,'','');
INSERT INTO ExistingCapacity VALUES('utopia','TXG',1970,3.100000000000000088,'','');
INSERT INTO ExistingCapacity VALUES('utopia','TXG',1980,1.5,'','');
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
INSERT INTO LoanLifetimeTech VALUES('utopia','E01',40.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','E21',40.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','E31',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','E51',100.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','E70',40.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','RHE',30.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','RHO',30.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','RL1',10.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','SRE',50.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','TXD',15.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','TXE',15.0,'');
INSERT INTO LoanLifetimeTech VALUES('utopia','TXG',15.0,'');
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
INSERT INTO LifetimeProcess VALUES('utopia','RL1',1980,20.0,'#forexistingcap');
INSERT INTO LifetimeProcess VALUES('utopia','TXD',1970,30.0,'#forexistingcap');
INSERT INTO LifetimeProcess VALUES('utopia','TXD',1980,30.0,'#forexistingcap');
INSERT INTO LifetimeProcess VALUES('utopia','TXG',1970,30.0,'#forexistingcap');
INSERT INTO LifetimeProcess VALUES('utopia','TXG',1980,30.0,'#forexistingcap');
CREATE TABLE LifetimeTech
(
    region   TEXT,
    tech     TEXT
        REFERENCES Technology (tech),
    lifetime REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO LifetimeTech VALUES('utopia','E01',40.0,'');
INSERT INTO LifetimeTech VALUES('utopia','E21',40.0,'');
INSERT INTO LifetimeTech VALUES('utopia','E31',100.0,'');
INSERT INTO LifetimeTech VALUES('utopia','E51',100.0,'');
INSERT INTO LifetimeTech VALUES('utopia','E70',40.0,'');
INSERT INTO LifetimeTech VALUES('utopia','RHE',30.0,'');
INSERT INTO LifetimeTech VALUES('utopia','RHO',30.0,'');
INSERT INTO LifetimeTech VALUES('utopia','RL1',10.0,'');
INSERT INTO LifetimeTech VALUES('utopia','SRE',50.0,'');
INSERT INTO LifetimeTech VALUES('utopia','TXD',15.0,'');
INSERT INTO LifetimeTech VALUES('utopia','TXE',15.0,'');
INSERT INTO LifetimeTech VALUES('utopia','TXG',15.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPDSL1',1000.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPGSL1',1000.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPHCO1',1000.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPOIL1',1000.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPURN1',1000.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPHYD',1000.0,'');
INSERT INTO LifetimeTech VALUES('utopia','IMPFEQ',1000.0,'');
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
INSERT INTO MaxCapacity VALUES('utopia',1990,'E31',0.1300000000000000044,'','');
INSERT INTO MaxCapacity VALUES('utopia',2000,'E31',0.1700000000000000122,'','');
INSERT INTO MaxCapacity VALUES('utopia',2010,'E31',0.2099999999999999923,'','');
INSERT INTO MaxCapacity VALUES('utopia',1990,'RHE',0.0,'','');
INSERT INTO MaxCapacity VALUES('utopia',1990,'TXD',0.5999999999999999778,'','');
INSERT INTO MaxCapacity VALUES('utopia',2000,'TXD',1.760000000000000008,'','');
INSERT INTO MaxCapacity VALUES('utopia',2010,'TXD',4.759999999999999787,'','');
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
INSERT INTO MinCapacity VALUES('utopia',1990,'E31',0.1300000000000000044,'','');
INSERT INTO MinCapacity VALUES('utopia',2000,'E31',0.1300000000000000044,'','');
INSERT INTO MinCapacity VALUES('utopia',2010,'E31',0.1300000000000000044,'','');
INSERT INTO MinCapacity VALUES('utopia',1990,'SRE',0.1000000000000000055,'','');
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
INSERT INTO Region VALUES('utopia',NULL);
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
INSERT INTO TimeSegmentFraction VALUES('inter','day',0.166699999999999987,'# I-D');
INSERT INTO TimeSegmentFraction VALUES('inter','night',0.08329999999999999905,'# I-N');
INSERT INTO TimeSegmentFraction VALUES('summer','day',0.166699999999999987,'# S-D');
INSERT INTO TimeSegmentFraction VALUES('summer','night',0.08329999999999999905,'# S-N');
INSERT INTO TimeSegmentFraction VALUES('winter','day',0.3332999999999999852,'# W-D');
INSERT INTO TimeSegmentFraction VALUES('winter','night',0.166699999999999987,'# W-N');
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
CREATE TABLE StorageInit
(
    tech  TEXT
        PRIMARY KEY,
    value REAL,
    notes TEXT
);
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
CREATE TABLE TechInputSplit
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
CREATE TABLE TechInputSplitAnnual
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
CREATE TABLE TechOutputSplit
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
INSERT INTO TechOutputSplit VALUES('utopia',1990,'SRE','DSL',0.6999999999999999556,'');
INSERT INTO TechOutputSplit VALUES('utopia',2000,'SRE','DSL',0.6999999999999999556,'');
INSERT INTO TechOutputSplit VALUES('utopia',2010,'SRE','DSL',0.6999999999999999556,'');
INSERT INTO TechOutputSplit VALUES('utopia',1990,'SRE','GSL',0.2999999999999999889,'');
INSERT INTO TechOutputSplit VALUES('utopia',2000,'SRE','GSL',0.2999999999999999889,'');
INSERT INTO TechOutputSplit VALUES('utopia',2010,'SRE','GSL',0.2999999999999999889,'');
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
INSERT INTO TimePeriod VALUES(1,1960,'e');
INSERT INTO TimePeriod VALUES(2,1970,'e');
INSERT INTO TimePeriod VALUES(3,1980,'e');
INSERT INTO TimePeriod VALUES(4,1990,'f');
INSERT INTO TimePeriod VALUES(5,2000,'f');
INSERT INTO TimePeriod VALUES(6,2010,'f');
INSERT INTO TimePeriod VALUES(7,2020,'f');
CREATE TABLE TimeSeason
(
    sequence INTEGER UNIQUE,
    season   TEXT
        PRIMARY KEY
);
INSERT INTO TimeSeason VALUES(1,'inter');
INSERT INTO TimeSeason VALUES(2,'summer');
INSERT INTO TimeSeason VALUES(3,'winter');
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
INSERT INTO Technology VALUES('IMPDSL1','r','supply','petroleum','',1,0,0,0,0,0,0,0,' imported diesel');
INSERT INTO Technology VALUES('IMPGSL1','r','supply','petroleum','',1,0,0,0,0,0,0,0,' imported gasoline');
INSERT INTO Technology VALUES('IMPHCO1','r','supply','coal','',1,0,0,0,0,0,0,0,' imported coal');
INSERT INTO Technology VALUES('IMPOIL1','r','supply','petroleum','',1,0,0,0,0,0,0,0,' imported crude oil');
INSERT INTO Technology VALUES('IMPURN1','r','supply','nuclear','',1,0,0,0,0,0,0,0,' imported uranium');
INSERT INTO Technology VALUES('IMPFEQ','r','supply','petroleum','',1,0,0,0,0,0,0,0,' imported fossil equivalent');
INSERT INTO Technology VALUES('IMPHYD','r','supply','hydro','',1,0,0,0,0,0,0,0,' imported water -- doesnt exist in Utopia');
INSERT INTO Technology VALUES('E01','pb','electric','coal','',0,0,0,0,0,0,0,0,' coal power plant');
INSERT INTO Technology VALUES('E21','pb','electric','nuclear','',0,0,0,0,0,0,0,0,' nuclear power plant');
INSERT INTO Technology VALUES('E31','pb','electric','hydro','',0,0,0,0,0,0,0,0,' hydro power');
INSERT INTO Technology VALUES('E51','ps','electric','electric','',0,0,0,0,0,0,0,0,' electric storage');
INSERT INTO Technology VALUES('E70','p','electric','petroleum','',0,0,0,0,0,0,0,0,' diesel power plant');
INSERT INTO Technology VALUES('RHE','p','residential','electric','',0,0,0,0,0,0,0,0,' electric residential heating');
INSERT INTO Technology VALUES('RHO','p','residential','petroleum','',0,0,0,0,0,0,0,0,' diesel residential heating');
INSERT INTO Technology VALUES('RL1','p','residential','electric','',0,0,0,0,0,0,0,0,' residential lighting');
INSERT INTO Technology VALUES('SRE','p','supply','petroleum','',0,0,0,0,0,0,0,0,' crude oil processor');
INSERT INTO Technology VALUES('TXD','p','transport','petroleum','',0,0,0,0,0,0,0,0,' diesel powered vehicles');
INSERT INTO Technology VALUES('TXE','p','transport','electric','',0,0,0,0,0,0,0,0,' electric powered vehicles');
INSERT INTO Technology VALUES('TXG','p','transport','petroleum','',0,0,0,0,0,0,0,0,' gasoline powered vehicles');
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
