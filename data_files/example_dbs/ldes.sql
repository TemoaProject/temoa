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
INSERT INTO MetaData VALUES ('days_per_period', 365, 'count of days in each period');
CREATE TABLE MetaDataReal
(
    element TEXT,
    value   REAL,
    notes   TEXT,

    PRIMARY KEY (element)
);
INSERT INTO MetaDataReal VALUES('global_discount_rate',0.05,'Discount Rate for future costs');
INSERT INTO MetaDataReal VALUES('default_loan_rate',0.05,'Default Loan Rate if not specified in LoanRate table');
CREATE TABLE OutputDualVariable
(
    scenario        TEXT,
    constraint_name TEXT,
    dual            REAL,
    PRIMARY KEY (constraint_name, scenario)
);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,d,generator,2000]',-0.085703001173645247945);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,d,demand,2000]',-0.00023042368874485079643);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,d,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,b,generator,2000]',-0.085357366392446838432);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,a,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,c,generator,2000]',-0.085703001174349608959);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,b,generator,2000]',-0.11558070679412910664);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,c,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,c,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,b,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,b,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,c,generator,2000]',-0.11558070712241454991);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,a,generator,2000]',-0.08535736638981534341);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,a,generator,2000]',-0.11558070668246853696);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,discharge,d,generator,2000]',-0.11558070724338096457);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityConstraint[region,2000,charge,a,demand,2000]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityAvailableByPeriodAndTechConstraint[region,2000,seas_stor]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityAvailableByPeriodAndTechConstraint[region,2000,generator]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityAvailableByPeriodAndTechConstraint[region,2000,demand]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','CapacityAvailableByPeriodAndTechConstraint[region,2000,dly_stor]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','AdjustedCapacityConstraint[region,2000,seas_stor,2000]',-25.231393917561169004);
INSERT INTO OutputDualVariable VALUES('zulu','AdjustedCapacityConstraint[region,2000,demand,2000]',-0.25231393917561169004);
INSERT INTO OutputDualVariable VALUES('zulu','AdjustedCapacityConstraint[region,2000,dly_stor,2000]',-0.25231393917561169004);
INSERT INTO OutputDualVariable VALUES('zulu','AdjustedCapacityConstraint[region,2000,generator,2000]',-252.31393917561164563);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,charge,b,demand]',8.7443107076524206888);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,charge,c,demand]',8.7446563424276391174);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,charge,a,demand]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,discharge,a,demand]',0.0);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,discharge,d,demand]',8.7747644720271349427);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,discharge,b,demand]',8.7745340480390616733);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,discharge,c,demand]',8.7745340482176992225);
INSERT INTO OutputDualVariable VALUES('zulu','DemandConstraint[region,2000,charge,d,demand]',8.7446563424269339037);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,charge,b,electricity]',4.4148340370215981565);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,charge,c,electricity]',4.4151796717968148087);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,discharge,a,electricity]',4.44505737729657735);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,charge,a,electricity]',4.4148340370189664838);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,discharge,d,electricity]',4.4450573777075668147);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,discharge,b,electricity]',4.4450573774082373645);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,discharge,c,electricity]',4.4450573775868758019);
INSERT INTO OutputDualVariable VALUES('zulu','CommodityBalanceConstraint[region,2000,charge,d,electricity]',4.4151796717961104832);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyConstraint[region,2000,winter,seas_stor,2000]',-4.4329123900165026128);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyConstraint[region,2000,summer,seas_stor,2000]',-4.4329123900150158021);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,winter,c,seas_stor,2000]',-9.9285300719515330314e-13);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,winter,a,seas_stor,2000]',-2.2220266853952255203e-12);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,summer,d,seas_stor,2000]',-1.3760422345105398633e-12);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,winter,d,seas_stor,2000]',-7.7749544304990836351e-13);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,summer,c,seas_stor,2000]',-9.928636176739285446e-13);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,summer,a,seas_stor,2000]',-6.3758520034707890644e-13);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,winter,b,seas_stor,2000]',-1.3731094778566776959e-12);
INSERT INTO OutputDualVariable VALUES('zulu','SeasonalStorageEnergyUpperBoundConstraint[region,2000,summer,b,seas_stor,2000]',-7.7654566423139437247e-13);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,c,seas_stor,2000]',6.4416949203073858853e-13);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,b,seas_stor,2000]',6.6523075894421745957e-13);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,b,seas_stor,2000]',-4.7138287749897429534e-13);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,c,dly_stor,2000]',4.4151796717729769881);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,b,dly_stor,2000]',4.4148340370445753322);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,a,dly_stor,2000]',4.4148340370562451084);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,a,seas_stor,2000]',8.1624677449077918112e-14);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,a,seas_stor,2000]',8.8939163809495713763e-14);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,d,dly_stor,2000]',4.415179671760228075);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,c,dly_stor,2000]',4.4450573775854937963);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,a,dly_stor,2000]',4.4450573773388573073);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,charge,c,seas_stor,2000]',-5.821732668700695612e-13);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,b,dly_stor,2000]',4.4450573774107144942);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyConstraint[region,2000,discharge,d,dly_stor,2000]',4.4450573776637751777);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,charge,c,dly_stor,2000]',-0.00034563473280713847834);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,charge,b,dly_stor,2000]',-4.5045066420029851173e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,charge,a,dly_stor,2000]',-1.8570385267138625806e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,charge,d,dly_stor,2000]',-4.4825967675597020445e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,discharge,c,dly_stor,2000]',-1.7883284614710022175e-10);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,discharge,a,dly_stor,2000]',-3.7581557153964029183e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,discharge,b,dly_stor,2000]',-7.6405648911312447069e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageEnergyUpperBoundConstraint[region,2000,discharge,d,dly_stor,2000]',-8.2734689766129356769e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,c,seas_stor,2000]',-3.5654595609390025146e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,b,seas_stor,2000]',-3.565273019415246658e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,d,seas_stor,2000]',-3.5649814908001054014e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,b,seas_stor,2000]',-0.0019150055793566611583);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,c,dly_stor,2000]',-4.1883387800486087115e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,b,dly_stor,2000]',-1.2069762722145627176e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,a,dly_stor,2000]',-1.7983916895994889628e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,a,seas_stor,2000]',-3.5651827068338381998e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,a,seas_stor,2000]',-0.0019557996514695448198);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,d,dly_stor,2000]',-3.9485685665929972643e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,d,seas_stor,2000]',-0.0018038898687766034001);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,c,dly_stor,2000]',-5.2294209073905513207e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,a,dly_stor,2000]',-2.016437280362393114e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,charge,c,seas_stor,2000]',-0.0017703732824977256754);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,b,dly_stor,2000]',-5.7797571613751692609e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageChargeRateConstraint[region,2000,discharge,d,dly_stor,2000]',-3.87006737036306383e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,c,seas_stor,2000]',-7.0883085262919003355e-09);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,b,seas_stor,2000]',-7.1579661355912342912e-09);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,d,seas_stor,2000]',-7.3829319339268231203e-09);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,b,seas_stor,2000]',-3.5613176789246074882e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,c,dly_stor,2000]',-1.2349788608388929667e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,b,dly_stor,2000]',-4.1884293092433901861e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,a,dly_stor,2000]',-3.9481261846979931462e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,a,seas_stor,2000]',-7.1347346464973728785e-09);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,a,seas_stor,2000]',-3.5613135641518733898e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,d,dly_stor,2000]',-1.7515961681002181649e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,d,seas_stor,2000]',-3.5610586195680133947e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,c,dly_stor,2000]',-5.7082184017434425271e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,a,dly_stor,2000]',-3.8795740106759190268e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,charge,c,seas_stor,2000]',-3.5610355629010550515e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,b,dly_stor,2000]',-5.1906403614485796538e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageDischargeRateConstraint[region,2000,discharge,d,dly_stor,2000]',-2.0711911733338417285e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,c,seas_stor,2000]',-1.5032898104432781849e-08);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,b,seas_stor,2000]',-1.4784579164256117067e-08);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,d,seas_stor,2000]',-1.4859608725011574925e-08);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,b,seas_stor,2000]',-0.0040183819650553598279);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,c,dly_stor,2000]',-1.5889638444455924215e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,b,dly_stor,2000]',-1.5380000139594174335e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,a,dly_stor,2000]',-2.2855346485298646541e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,a,seas_stor,2000]',-1.4696732922444764035e-08);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,a,seas_stor,2000]',-0.0039775878961343966722);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,d,dly_stor,2000]',-2.1971314167586482035e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,d,seas_stor,2000]',-0.0037838629015935030253);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,c,dly_stor,2000]',-8.1736320692959303357e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,a,dly_stor,2000]',-2.5498616661417998763e-11);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,charge,c,seas_stor,2000]',-0.0038173794865856454094);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,b,dly_stor,2000]',-8.2337089532251290791e-12);
INSERT INTO OutputDualVariable VALUES('zulu','StorageThroughputConstraint[region,2000,discharge,d,dly_stor,2000]',-2.6432678697009204249e-11);
CREATE TABLE OutputObjective
(
    scenario          TEXT,
    objective_name    TEXT,
    total_system_cost REAL
);
INSERT INTO OutputObjective VALUES('zulu','TotalCost',76813.228544347014192);
CREATE TABLE SectorLabel
(
    sector TEXT,
    PRIMARY KEY (sector)
);
INSERT INTO SectorLabel VALUES('electricity');
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
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES TimeSeason (season),
    tod    TEXT
        REFERENCES TimeOfDay (tod),
    tech   TEXT
        REFERENCES Technology (tech),
    factor REAL,
    notes  TEXT,
    PRIMARY KEY (region, period, season, tod, tech),
    CHECK (factor >= 0 AND factor <= 1)
);
INSERT INTO CapacityFactorTech VALUES('region',2000,'charge','a','generator',1.0,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'charge','b','generator',1.0,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'charge','c','generator',0.2,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'charge','d','generator',0.2,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'discharge','a','generator',0.1,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'discharge','b','generator',0.1,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'discharge','c','generator',0.01,NULL);
INSERT INTO CapacityFactorTech VALUES('region',2000,'discharge','d','generator',0.01,NULL);
CREATE TABLE CapacityToActivity
(
    region TEXT,
    tech   TEXT
        REFERENCES Technology (tech),
    c2a    REAL,
    notes  TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO CapacityToActivity VALUES('region','generator',8760.0,'MWh/MWy');
INSERT INTO CapacityToActivity VALUES('region','dly_stor',8760.0,'MWh/MWy');
INSERT INTO CapacityToActivity VALUES('region','seas_stor',8760.0,'MWh/MWy');
INSERT INTO CapacityToActivity VALUES('region','demand',8760.0,'MWh/MWy');
CREATE TABLE Commodity
(
    name        TEXT
        PRIMARY KEY,
    flag        TEXT
        REFERENCES CommodityType (label),
    description TEXT
);
INSERT INTO Commodity VALUES('ethos','s',NULL);
INSERT INTO Commodity VALUES('electricity','p',NULL);
INSERT INTO Commodity VALUES('demand','d',NULL);
CREATE TABLE CommodityType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO CommodityType VALUES('p','physical commodity');
INSERT INTO CommodityType VALUES('a','annual commodity');
INSERT INTO CommodityType VALUES('e','emissions commodity');
INSERT INTO CommodityType VALUES('d','demand commodity');
INSERT INTO CommodityType VALUES('s','source commodity');
INSERT INTO CommodityType VALUES('w','waste commodity');
INSERT INTO CommodityType VALUES('wa','waste annual commodity');
INSERT INTO CommodityType VALUES('wp','waste physical commodity');
CREATE TABLE ConstructionInput
(
    region      TEXT,
    input_comm   TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, input_comm, tech, vintage)
);
CREATE TABLE CostEmission
(
    region    TEXT,
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
INSERT INTO CostInvest VALUES('region','generator',2000,1000.0,'',NULL);
INSERT INTO CostInvest VALUES('region','dly_stor',2000,1.0,'',NULL);
INSERT INTO CostInvest VALUES('region','seas_stor',2000,100.0,'',NULL);
INSERT INTO CostInvest VALUES('region','demand',2000,1.0,'',NULL);
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
INSERT INTO CostVariable VALUES('region',2000,'generator',2000,1.0,NULL,NULL);
INSERT INTO CostVariable VALUES('region',2000,'demand',2000,1.0,NULL,NULL);
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
INSERT INTO Demand VALUES('region',2000,'demand',8760.0,'MWh',NULL);
CREATE TABLE DemandSpecificDistribution
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    season      TEXT
        REFERENCES TimeSeason (season),
    tod         TEXT
        REFERENCES TimeOfDay (tod),
    demand_name TEXT
        REFERENCES Commodity (name),
    dsd         REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, demand_name),
    CHECK (dsd >= 0 AND dsd <= 1)
);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'charge','a','demand',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'charge','b','demand',0.05,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'charge','c','demand',0.05,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'charge','d','demand',0.1,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'discharge','a','demand',0.0,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'discharge','b','demand',0.2,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'discharge','c','demand',0.2,NULL);
INSERT INTO DemandSpecificDistribution VALUES('region',2000,'discharge','d','demand',0.4,NULL);
CREATE TABLE EndOfLifeOutput
(
    region      TEXT,
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    output_comm   TEXT
        REFERENCES Commodity (name),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, tech, vintage, output_comm)
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
INSERT INTO Efficiency VALUES('region','ethos','generator',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('region','electricity','dly_stor',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('region','electricity','seas_stor',2000,'electricity',1.0,NULL);
INSERT INTO Efficiency VALUES('region','electricity','demand',2000,'demand',1.0,NULL);
CREATE TABLE EfficiencyVariable
(
    region      TEXT,
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
    efficiency  REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, season, tod, input_comm, tech, vintage, output_comm),
    CHECK (efficiency > 0)
);
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
CREATE TABLE EmissionEmbodied
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm,  tech, vintage)
);
CREATE TABLE EmissionEndOfLife
(
    region      TEXT,
    emis_comm   TEXT
        REFERENCES Commodity (name),
    tech        TEXT
        REFERENCES Technology (tech),
    vintage     INTEGER
        REFERENCES TimePeriod (period),
    value       REAL,
    units       TEXT,
    notes       TEXT,
    PRIMARY KEY (region, emis_comm,  tech, vintage)
);
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
CREATE TABLE TechGroup
(
    group_name TEXT
        PRIMARY KEY,
    notes      TEXT
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
CREATE TABLE Operator
(
	operator TEXT PRIMARY KEY,
	notes TEXT
);
INSERT INTO Operator VALUES('e','equal to');
INSERT INTO Operator VALUES('le','less than or equal to');
INSERT INTO Operator VALUES('ge','greater than or equal to');
CREATE TABLE LimitGrowthCapacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitDegrowthCapacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitGrowthNewCapacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitDegrowthNewCapacity
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitGrowthNewCapacityDelta
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitDegrowthNewCapacityDelta
(
    region TEXT,
    tech_or_group   TEXT,
    operator TEXT NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    rate   REAL NOT NULL DEFAULT 0,
    seed   REAL NOT NULL DEFAULT 0,
    seed_units TEXT,
    notes  TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitStorageLevelFraction
(
    region   TEXT,
    period   INTEGER
        REFERENCES TimePeriod (period),
    season   TEXT
        REFERENCES TimeSeason (season),
    tod      TEXT
        REFERENCES TimeOfDay (tod),
    tech     TEXT
        REFERENCES Technology (tech),
    vintage  INTEGER
        REFERENCES TimePeriod (period),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    fraction REAL,
    notes    TEXT,
    PRIMARY KEY(region, period, season, tod, tech, vintage, operator)
);
CREATE TABLE LimitActivity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    activity REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE LimitActivityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE LimitAnnualCapacityFactor
(
    region      TEXT,
    period      INTEGER
        REFERENCES TimePeriod (period),
    tech        TEXT
        REFERENCES Technology (tech),
    output_comm TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    factor      REAL,
    notes       TEXT,
    PRIMARY KEY (region, period, tech, operator),
    CHECK (factor >= 0 AND factor <= 1)
);
CREATE TABLE LimitCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    capacity REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE LimitCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE LimitNewCapacity
(
    region  TEXT,
    period  INTEGER
        REFERENCES TimePeriod (period),
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    new_cap REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, period, tech_or_group, operator)
);
CREATE TABLE LimitNewCapacityShare
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    sub_group      TEXT,
    super_group    TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    share REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, sub_group, super_group, operator)
);
CREATE TABLE LimitResource
(
    region  TEXT,
    tech_or_group   TEXT,
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    cum_act REAL,
    units   TEXT,
    notes   TEXT,
    PRIMARY KEY (region, tech_or_group, operator)
);
CREATE TABLE LimitSeasonalCapacityFactor
(
	region  TEXT
        REFERENCES Region (region),
	period	INTEGER
        REFERENCES TimePeriod (period),
	season	TEXT
        REFERENCES TimeSeason (season),
	tech    TEXT
        REFERENCES Technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
	factor	REAL,
	notes	TEXT,
	PRIMARY KEY(region, period, season, tech, operator)
);
CREATE TABLE LimitTechInputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
CREATE TABLE LimitTechInputSplitAnnual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    input_comm     TEXT
        REFERENCES Commodity (name),
    tech           TEXT
        REFERENCES Technology (tech),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, input_comm, tech, operator)
);
CREATE TABLE LimitTechOutputSplit
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
CREATE TABLE LimitTechOutputSplitAnnual
(
    region         TEXT,
    period         INTEGER
        REFERENCES TimePeriod (period),
    tech           TEXT
        REFERENCES Technology (tech),
    output_comm    TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    proportion REAL,
    notes          TEXT,
    PRIMARY KEY (region, period, tech, output_comm, operator)
);
CREATE TABLE LimitEmission
(
    region    TEXT,
    period    INTEGER
        REFERENCES TimePeriod (period),
    emis_comm TEXT
        REFERENCES Commodity (name),
    operator	TEXT  NOT NULL DEFAULT "le"
    	REFERENCES Operator (operator),
    value     REAL,
    units     TEXT,
    notes     TEXT,
    PRIMARY KEY (region, period, emis_comm, operator)
);
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
INSERT INTO OutputNetCapacity VALUES('zulu','region','electricity',2000,'seas_stor',2000,1.4392656320725425445);
INSERT INTO OutputNetCapacity VALUES('zulu','region','electricity',2000,'demand',2000,3.2000000000000001776);
INSERT INTO OutputNetCapacity VALUES('zulu','region','electricity',2000,'dly_stor',2000,4.2785306855583380425);
INSERT INTO OutputNetCapacity VALUES('zulu','region','electricity',2000,'generator',2000,3.0654425023163081043);
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
INSERT INTO OutputBuiltCapacity VALUES('zulu','region','electricity','seas_stor',2000,1.4392656320725425445);
INSERT INTO OutputBuiltCapacity VALUES('zulu','region','electricity','demand',2000,3.2000000000000001776);
INSERT INTO OutputBuiltCapacity VALUES('zulu','region','electricity','generator',2000,3.0654425023163081043);
INSERT INTO OutputBuiltCapacity VALUES('zulu','region','electricity','dly_stor',2000,4.2785306855583380425);
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
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','d','electricity','seas_stor',2000,'electricity',1.6658229082653559061);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','b','electricity','seas_stor',2000,'electricity',1575.9958575418115955);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','a','electricity','seas_stor',2000,'electricity',1575.9958579731961236);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','d','electricity','seas_stor',2000,'electricity',1575.9956575478158313);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','c','electricity','seas_stor',2000,'electricity',1.8910884059675414192);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','c','electricity','dly_stor',2000,'electricity',1204.7596747035338449);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','a','electricity','dly_stor',2000,'electricity',2618.5087591179661004);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','c','electricity','dly_stor',2000,'electricity',851.96387645265332366);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','b','electricity','dly_stor',2000,'electricity',2188.5411244155807963);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','c','electricity','seas_stor',2000,'electricity',1575.9956514181672204);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','b','electricity','seas_stor',2000,'electricity',1.798751859454663915);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','d','electricity','dly_stor',2000,'electricity',735.89264698708465317);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','a','electricity','seas_stor',2000,'electricity',1.7546442646897240535);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','a','electricity','dly_stor',2000,'electricity',2523.3859171065073923);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','d','electricity','dly_stor',2000,'electricity',719.1263802165781982);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','b','electricity','dly_stor',2000,'electricity',1363.0051112588996709);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','c','electricity','demand',2000,'demand',1752.0);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','d','electricity','demand',2000,'demand',3504.0);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','c','ethos','generator',2000,'electricity',33.566595265745142739);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','d','electricity','demand',2000,'demand',876.0);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','b','electricity','demand',2000,'demand',1752.0);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','a','ethos','generator',2000,'electricity',3356.6595399160439328);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','b','electricity','demand',2000,'demand',438.0);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','b','ethos','generator',2000,'electricity',3356.6595399162086899);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','d','ethos','generator',2000,'electricity',33.566595289722491735);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','a','ethos','generator',2000,'electricity',335.66595390483335847);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','d','ethos','generator',2000,'electricity',671.33190787721055414);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'discharge','b','ethos','generator',2000,'electricity',335.66595390600832971);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','c','ethos','generator',2000,'electricity',671.33190787684080547);
INSERT INTO OutputFlowIn VALUES('zulu','region','electricity',2000,'charge','c','electricity','demand',2000,'demand',438.0);
CREATE TABLE OutputFlowOut
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
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','d','electricity','seas_stor',2000,'electricity',1568.9482946398751295);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','d','electricity','seas_stor',2000,'electricity',5.895025229563088942e-05);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','c','electricity','seas_stor',2000,'electricity',1568.6232908987555845);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','c','electricity','dly_stor',2000,'electricity',1356.4608769452966008);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','a','electricity','dly_stor',2000,'electricity',714.83103160110816887);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','c','electricity','dly_stor',2000,'electricity',2194.6275577242486676);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','b','electricity','dly_stor',2000,'electricity',845.87743847871745828);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','c','electricity','seas_stor',2000,'electricity',6.2268121432416947413e-05);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','b','electricity','seas_stor',2000,'electricity',1569.3072056574608907);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','d','electricity','dly_stor',2000,'electricity',2516.5563377074744444);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','a','electricity','seas_stor',2000,'electricity',1569.7664178764727083);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','a','electricity','dly_stor',2000,'electricity',742.72223105128469811);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','d','electricity','dly_stor',2000,'electricity',2622.2773131962147097);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','b','electricity','dly_stor',2000,'electricity',1211.8307035541360239);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','c','electricity','demand',2000,'demand',1752.0);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','d','electricity','demand',2000,'demand',3504.0);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','c','ethos','generator',2000,'electricity',33.566595265745142739);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','d','electricity','demand',2000,'demand',876.0);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','b','electricity','demand',2000,'demand',1752.0);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','a','ethos','generator',2000,'electricity',3356.6595399160439328);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','b','electricity','demand',2000,'demand',438.0);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','b','ethos','generator',2000,'electricity',3356.6595399162086899);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','d','ethos','generator',2000,'electricity',33.566595289722491735);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','a','ethos','generator',2000,'electricity',335.66595390483335847);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','d','ethos','generator',2000,'electricity',671.33190787721055414);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'discharge','b','ethos','generator',2000,'electricity',335.66595390600832971);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','c','ethos','generator',2000,'electricity',671.33190787684080547);
INSERT INTO OutputFlowOut VALUES('zulu','region','electricity',2000,'charge','c','electricity','demand',2000,'demand',438.0);
CREATE TABLE OutputStorageLevel
(
    scenario TEXT,
    region TEXT,
    sector TEXT
        REFERENCES SectorLabel (sector),
    period INTEGER
        REFERENCES TimePeriod (period),
    season TEXT
        REFERENCES TimeSeason (season),
    tod TEXT
        REFERENCES TimeOfDay (tod),
    tech TEXT
        REFERENCES Technology (tech),
    vintage INTEGER
        REFERENCES TimePeriod (period),
    level REAL,
    PRIMARY KEY (scenario, region, period, season, tod, tech, vintage)
);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'charge','c','dly_stor',2000,17.114122593311056341);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'charge','b','dly_stor',2000,9.7570613005062956091);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'charge','a','dly_stor',2000,0.0);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'charge','d','dly_stor',2000,9.7570613260688681123);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'discharge','c','dly_stor',2000,14.713232852985489884);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'discharge','a','dly_stor',2000,3.4537690983471556194);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'discharge','b','dly_stor',2000,13.884879934054414896);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'discharge','d','dly_stor',2000,13.881993388646614029);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'winter','a','seas_stor',2000,10085.458960857824894);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'winter','b','seas_stor',2000,8517.4471872485479906);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'winter','c','seas_stor',2000,6949.9387334479445499);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'winter','d','seas_stor',2000,5383.206530959131264);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'summer','a','seas_stor',2000,3798.7472513029865162);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'summer','b','seas_stor',2000,5374.7431051676910485);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'summer','c','seas_stor',2000,6950.7389591488673019);
INSERT INTO OutputStorageLevel VALUES('zulu','region','electricity',2000,'summer','d','seas_stor',2000,8526.734548299248928);
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
INSERT INTO Region VALUES('region',NULL);
CREATE TABLE TimeSegmentFraction
(   
    period INTEGER
        REFERENCES TimePeriod (period),
    season  TEXT
        REFERENCES TimeSeason (season),
    tod     TEXT
        REFERENCES TimeOfDay (tod),
    segfrac REAL,
    notes   TEXT,
    PRIMARY KEY (period, season, tod),
    CHECK (segfrac >= 0 AND segfrac <= 1)
);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','a',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','b',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','c',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'charge','d',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','a',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','b',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','c',0.125,NULL);
INSERT INTO TimeSegmentFraction VALUES(2000,'discharge','d',0.125,NULL);
CREATE TABLE StorageDuration
(
    region   TEXT,
    tech     TEXT,
    duration REAL,
    notes    TEXT,
    PRIMARY KEY (region, tech)
);
INSERT INTO StorageDuration VALUES('region','dly_stor',4.0,NULL);
INSERT INTO StorageDuration VALUES('region','seas_stor',8760.0,NULL);
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
CREATE TABLE TimeOfDay
(
    sequence INTEGER UNIQUE,
    tod      TEXT
        PRIMARY KEY
);
INSERT INTO TimeOfDay VALUES(0,'a');
INSERT INTO TimeOfDay VALUES(1,'b');
INSERT INTO TimeOfDay VALUES(2,'c');
INSERT INTO TimeOfDay VALUES(3,'d');
CREATE TABLE TimePeriod
(
    sequence INTEGER UNIQUE,
    period   INTEGER
        PRIMARY KEY,
    flag     TEXT
        REFERENCES TimePeriodType (label)
);
INSERT INTO TimePeriod VALUES(0,2000,'f');
INSERT INTO TimePeriod VALUES(1,2005,'f');
CREATE TABLE TimeSeason
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    season TEXT,
    notes TEXT,
    PRIMARY KEY (period, sequence, season)
);
INSERT INTO TimeSeason VALUES(2000,0,'charge',NULL);
INSERT INTO TimeSeason VALUES(2000,1,'discharge',NULL);
CREATE TABLE TimePeriodType
(
    label       TEXT
        PRIMARY KEY,
    description TEXT
);
INSERT INTO TimePeriodType VALUES('e','existing vintages');
INSERT INTO TimePeriodType VALUES('f','future');
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
    exchange     INTEGER NOT NULL DEFAULT 0,
    seas_stor    INTEGER NOT NULL DEFAULT 0,
    description  TEXT,
    FOREIGN KEY (flag) REFERENCES TechnologyType (label)
);
INSERT INTO Technology VALUES('generator','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('dly_stor','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
INSERT INTO Technology VALUES('seas_stor','ps','electricity',NULL,NULL,0,0,0,0,0,0,0,1,NULL);
INSERT INTO Technology VALUES('demand','p','electricity',NULL,NULL,0,0,0,0,0,0,0,0,NULL);
CREATE TABLE OutputCost
(
    scenario TEXT,
    region   TEXT,
    sector   TEXT REFERENCES SectorLabel (sector),
    period   INTEGER REFERENCES TimePeriod (period),
    tech     TEXT REFERENCES Technology (tech),
    vintage  INTEGER REFERENCES TimePeriod (period),
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
INSERT INTO OutputCost VALUES('zulu','region','electricity',2000,'demand',2000,0.80740460536195755025,0.0,37926.215634726010428,0.0,0.51801829986182648113,0.0,43800.0,0.0);
INSERT INTO OutputCost VALUES('zulu','region','electricity',2000,'dly_stor',2000,1.0795329311569543673,0.0,0.0,0.0,0.69261162238737030705,0.0,0.0,0.0);
INSERT INTO OutputCost VALUES('zulu','region','electricity',2000,'generator',2000,773.45387307577189162,0.0,38075.357420893887194,0.0,496.23603542939909161,0.0,43972.239969763071698,0.0);
INSERT INTO OutputCost VALUES('zulu','region','electricity',2000,'seas_stor',2000,36.314678114829974653,0.0,0.0,0.0,23.298935492992982609,0.0,0.0,0.0);
CREATE TABLE TimeStorageSeason
(
    period INTEGER
        REFERENCES TimePeriod (period),
    sequence INTEGER,
    storage_season TEXT,
    season TEXT
        REFERENCES TimeSeason (season),
    count NUMERIC NOT NULL,
    notes TEXT,
    PRIMARY KEY (period, sequence, storage_season, season),
    CHECK (count > 0)
);
INSERT INTO TimeStorageSeason VALUES(2000,1,'summer','charge',182.5,NULL);
INSERT INTO TimeStorageSeason VALUES(2000,3,'winter','discharge',182.5,NULL);
COMMIT;
