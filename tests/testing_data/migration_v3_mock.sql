-- Mock data for v3 -> v4 migration testing
INSERT INTO Region (region) VALUES ('R1');
INSERT OR IGNORE INTO TechnologyType (label, description) VALUES ('p', 'production');
INSERT INTO Technology (tech, flag, unlim_cap, annual, reserve, curtail, retire, flex, exchange) VALUES ('T1', 'p', 0, 0, 0, 0, 0, 0, 0);

INSERT INTO TimePeriodType (label, description) VALUES ('e', 'existing');
INSERT INTO TimePeriodType (label, description) VALUES ('f', 'future');
INSERT INTO TimePeriod (sequence, period, flag) VALUES (1, 2020, 'e');
INSERT INTO TimePeriod (sequence, period, flag) VALUES (2, 2030, 'f');
INSERT INTO TimePeriod (sequence, period, flag) VALUES (3, 2040, 'f');



INSERT INTO TimeOfDay (sequence, tod) VALUES (1, 'day');
INSERT INTO TimeOfDay (sequence, tod) VALUES (2, 'night');

INSERT INTO TimeSeason (sequence, season) VALUES (1, 'winter');
INSERT INTO TimeSeason (sequence, season) VALUES (2, 'summer');

INSERT INTO TimeSegmentFraction (season, tod, segfrac) VALUES ('winter', 'day', 0.2);
INSERT INTO TimeSegmentFraction (season, tod, segfrac) VALUES ('winter', 'night', 0.1);
INSERT INTO TimeSegmentFraction (season, tod, segfrac) VALUES ('summer', 'day', 0.4);
INSERT INTO TimeSegmentFraction (season, tod, segfrac) VALUES ('summer', 'night', 0.3);

INSERT OR IGNORE INTO CommodityType (label, description) VALUES ('p', 'physical');
INSERT INTO Commodity (name, flag) VALUES ('In', 'p');
INSERT INTO Commodity (name, flag) VALUES ('Out', 'p');

INSERT INTO CapacityFactorProcess (region, season, tod, tech, vintage, factor) VALUES ('R1', 'winter', 'day', 'T1', 2030, 0.6);
INSERT INTO Efficiency (region, input_comm, tech, vintage, output_comm, efficiency) VALUES ('R1', 'In', 'T1', 2030, 'Out', 0.9);
INSERT INTO MinCapacity (region, tech, period, min_cap, units, notes) VALUES ('R1', 'T1', 2030, 10.0, 'GW', 'test op');
INSERT INTO EmissionLimit (region, period, emis_comm, value, units, notes) VALUES ('R1', 2030, 'Out', 100.0, 'kt', 'test op');
