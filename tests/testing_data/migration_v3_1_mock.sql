-- Mock data for v3.1 -> v4 migration testing
INSERT INTO Region (region) VALUES ('R1');
INSERT OR IGNORE INTO TechnologyType (label, description) VALUES ('p', 'production');
INSERT INTO Technology (tech, flag, unlim_cap, annual, reserve, curtail, retire, flex, exchange, seas_stor) VALUES ('T1', 'p', 0, 0, 0, 0, 0, 0, 0, 0);

INSERT INTO TimePeriod (sequence, period, flag) VALUES (1, 2020, 'e');
INSERT INTO TimePeriod (sequence, period, flag) VALUES (2, 2030, 'f');
INSERT INTO TimePeriod (sequence, period, flag) VALUES (3, 2040, 'f');

INSERT INTO SeasonLabel (season) VALUES ('winter');
INSERT INTO SeasonLabel (season) VALUES ('summer');

INSERT INTO TimeOfDay (sequence, tod) VALUES (1, 'day');
INSERT INTO TimeOfDay (sequence, tod) VALUES (2, 'night');

INSERT INTO TimeSeason (period, sequence, season) VALUES (2030, 1, 'winter');
INSERT INTO TimeSeason (period, sequence, season) VALUES (2030, 2, 'summer');

INSERT INTO TimeSegmentFraction (period, season, tod, segfrac) VALUES (2030, 'winter', 'day', 0.2);
INSERT INTO TimeSegmentFraction (period, season, tod, segfrac) VALUES (2030, 'winter', 'night', 0.1);
INSERT INTO TimeSegmentFraction (period, season, tod, segfrac) VALUES (2030, 'summer', 'day', 0.4);
INSERT INTO TimeSegmentFraction (period, season, tod, segfrac) VALUES (2030, 'summer', 'night', 0.3);

INSERT OR IGNORE INTO CommodityType (label, description) VALUES ('p', 'physical');
INSERT INTO Commodity (name, flag) VALUES ('In', 'p');
INSERT INTO Commodity (name, flag) VALUES ('Out', 'p');

INSERT INTO CapacityFactorProcess (region, period, season, tod, tech, vintage, factor) VALUES ('R1', 2030, 'winter', 'day', 'T1', 2030, 0.5);
INSERT INTO CapacityFactorProcess (region, period, season, tod, tech, vintage, factor) VALUES ('R1', 2040, 'winter', 'day', 'T1', 2030, 0.7);
INSERT INTO Efficiency (region, input_comm, tech, vintage, output_comm, efficiency) VALUES ('R1', 'In', 'T1', 2030, 'Out', 0.9);
INSERT INTO LimitCapacity (region, period, tech_or_group, operator, capacity, units, notes) VALUES ('R1', 2030, 'T1', 'ge', 10.0, 'GW', 'test op');
INSERT INTO LimitEmission (region, period, emis_comm, operator, value, units, notes) VALUES ('R1', 2030, 'Out', 'le', 100.0, 'kt', 'test op');

-- Split tables (explicit seasonal/annual in v3.1) — verify placement survives migration.
INSERT INTO Technology (tech, flag, unlim_cap, annual, reserve, curtail, retire, flex, exchange, seas_stor) VALUES ('T2', 'p', 0, 1, 0, 0, 0, 0, 0, 0);
INSERT INTO Efficiency (region, input_comm, tech, vintage, output_comm, efficiency) VALUES ('R1', 'In', 'T2', 2030, 'Out', 0.9);
INSERT INTO LimitTechInputSplit (region, period, input_comm, tech, operator, proportion, notes) VALUES ('R1', 2030, 'In', 'T1', 'ge', 0.3, 'seasonal-tech split');
INSERT INTO LimitTechInputSplitAnnual (region, period, input_comm, tech, operator, proportion, notes) VALUES ('R1', 2030, 'In', 'T2', 'ge', 0.4, 'annual-tech split');
INSERT INTO LimitTechOutputSplit (region, period, tech, output_comm, operator, proportion, notes) VALUES ('R1', 2030, 'T1', 'Out', 'ge', 0.5, 'seasonal-tech split');
INSERT INTO LimitTechOutputSplitAnnual (region, period, tech, output_comm, operator, proportion, notes) VALUES ('R1', 2030, 'T2', 'Out', 'ge', 0.6, 'annual-tech split');
