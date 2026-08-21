-- Mock data for v4 -> v4.1 migration testing
PRAGMA foreign_keys = OFF;
INSERT OR IGNORE INTO commodity_type (label, description) VALUES ('p', 'physical');
INSERT OR IGNORE INTO commodity_type (label, description) VALUES ('e', 'emissions');
INSERT OR IGNORE INTO sector_label (sector) VALUES ('electric');

INSERT INTO commodity (name, flag) VALUES ('FuelIn', 'p');
INSERT INTO commodity (name, flag) VALUES ('EnergyOut', 'p');

INSERT INTO time_period (period, flag) VALUES (2020, 'e');
INSERT INTO time_period (period, flag) VALUES (2030, 'f');
INSERT INTO time_period (period, flag) VALUES (2040, 'f');

INSERT INTO time_season (season, segment_fraction) VALUES ('summer', 0.6);
INSERT INTO time_season (season, segment_fraction) VALUES ('winter', 0.4);

INSERT INTO time_of_day (tod, hours) VALUES ('day', 14.4);
INSERT INTO time_of_day (tod, hours) VALUES ('night', 9.6);

INSERT OR IGNORE INTO technology_type (label, description) VALUES ('p', 'production');
INSERT INTO technology (tech, flag, reserve) VALUES ('GasTurbine', 'p', 1);
INSERT INTO technology (tech, flag, reserve) VALUES ('WindFarm', 'p', 1);
INSERT INTO technology (tech, flag, reserve) VALUES ('CoalPlant', 'p', 0);

INSERT INTO efficiency (region, input_comm, tech, vintage, output_comm, efficiency)
    VALUES ('R1', 'FuelIn', 'GasTurbine', 2030, 'EnergyOut', 0.4);
INSERT INTO efficiency (region, input_comm, tech, vintage, output_comm, efficiency)
    VALUES ('R1', 'FuelIn', 'WindFarm', 2030, 'EnergyOut', 1.0);
INSERT INTO efficiency (region, input_comm, tech, vintage, output_comm, efficiency)
    VALUES ('R1', 'FuelIn', 'CoalPlant', 2030, 'EnergyOut', 0.35);

-- capacity_credit will migrate to planning_reserve_credit (dropping period, vintage)
INSERT INTO capacity_credit (region, period, tech, vintage, credit)
    VALUES ('R1', 2030, 'GasTurbine', 2030, 0.85);
INSERT INTO capacity_credit (region, period, tech, vintage, credit)
    VALUES ('R1', 2040, 'GasTurbine', 2030, 0.80);
INSERT INTO capacity_credit (region, period, tech, vintage, credit)
    VALUES ('R1', 2030, 'WindFarm', 2030, 0.25);

-- reserve_capacity_derate will migrate to operating_reserve_derate (dropping vintage)
INSERT INTO reserve_capacity_derate (region, season, tech, vintage, factor)
    VALUES ('R1', 'summer', 'GasTurbine', 2030, 0.95);
INSERT INTO reserve_capacity_derate (region, season, tech, vintage, factor)
    VALUES ('R1', 'summer', 'WindFarm', 2030, 0.20);
INSERT INTO reserve_capacity_derate (region, season, tech, vintage, factor)
    VALUES ('R1', 'winter', 'WindFarm', 2030, 0.10);

-- planning_reserve_margin will migrate using reserve-flagged tech group as tech_or_group
INSERT INTO planning_reserve_margin (region, margin) VALUES ('R1', 0.15);

-- rps_requirement will migrate to limit_activity_share
INSERT INTO tech_group (group_name) VALUES ('renewables');
INSERT INTO rps_requirement (region, period, tech_group, requirement)
    VALUES ('R1', 2030, 'renewables', 0.30);
INSERT INTO rps_requirement (region, period, tech_group, requirement)
    VALUES ('R1', 2040, 'renewables', 0.40);
