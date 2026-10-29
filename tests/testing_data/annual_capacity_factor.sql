-- A single investible cohort, two five-year operating periods, no replacement.
-- With demand 1 and C2A 1, le factors 0.5/0.25 require capacity 4 (0.5/0.5: 2).
INSERT INTO region (region) VALUES ('R1');
INSERT INTO sector_label (sector) VALUES ('transport');
INSERT INTO time_period VALUES (0, 2025, 'f'), (1, 2030, 'f'), (2, 2035, 'f');
INSERT INTO time_season (sequence, season, segment_fraction) VALUES (0, 'S', 1);
INSERT INTO time_of_day (sequence, tod, hours) VALUES (0, 'day', 12), (1, 'night', 12);
INSERT INTO commodity (name, flag) VALUES ('source', 's'), ('service', 'd');
INSERT INTO technology (tech, flag, sector, annual) VALUES ('vehicle', 'p', 'transport', 1);
INSERT INTO efficiency (region, input_comm, tech, vintage, output_comm, efficiency)
VALUES ('R1', 'source', 'vehicle', 2025, 'service', 1);
INSERT INTO capacity_to_activity (region, tech, c2a) VALUES ('R1', 'vehicle', 1);
INSERT INTO cost_invest (region, tech, vintage, cost) VALUES ('R1', 'vehicle', 2025, 1);
INSERT INTO loan_lifetime_process (region, tech, vintage, lifetime)
VALUES ('R1', 'vehicle', 2025, 10);
INSERT INTO lifetime_tech (region, tech, lifetime) VALUES ('R1', 'vehicle', 10);
INSERT INTO demand (region, period, commodity, demand)
VALUES ('R1', 2025, 'service', 1), ('R1', 2030, 'service', 1);
-- Named old-column inserts intentionally exercise the compatibility contract.
INSERT INTO limit_annual_capacity_factor
    (region, tech_or_group, vintage, output_comm, operator, factor)
VALUES ('R1', 'vehicle', 2025, 'service', 'le', 0.5);
