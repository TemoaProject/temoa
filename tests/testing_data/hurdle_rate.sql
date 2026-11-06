-- Invented equipment example: one annual demand, two ways to supply it.
INSERT INTO region(region) VALUES ('region');
INSERT INTO sector_label(sector) VALUES ('equipment');
INSERT INTO commodity(name, flag) VALUES ('source', 's'), ('demand', 'd');
INSERT INTO technology(tech, flag, sector) VALUES
    ('standard', 'p', 'equipment'), ('efficient', 'p', 'equipment');
INSERT INTO time_period(sequence, period, flag) VALUES (0, 2020, 'f'), (1, 2035, 'f');
INSERT INTO time_season(sequence, season, segment_fraction) VALUES (0, 'year', 1);
INSERT INTO time_of_day(sequence, tod, hours) VALUES (0, 'day', 24);
INSERT INTO demand(region, period, commodity, demand) VALUES ('region', 2020, 'demand', 1);
INSERT INTO efficiency(region, input_comm, tech, vintage, output_comm, efficiency) VALUES
    ('region', 'source', 'standard', 2020, 'demand', 1),
    ('region', 'source', 'efficient', 2020, 'demand', 1);
INSERT INTO cost_invest(region, tech, vintage, cost) VALUES
    ('region', 'standard', 2020, 1000), ('region', 'efficient', 2020, 1500);
INSERT INTO cost_variable(region, period, tech, vintage, cost) VALUES
    ('region', 2020, 'standard', 2020, 300), ('region', 2020, 'efficient', 2020, 240);
INSERT INTO lifetime_tech(region, tech, lifetime) VALUES
    ('region', 'standard', 15), ('region', 'efficient', 15);
INSERT INTO loan_lifetime_process(region, tech, vintage, lifetime) VALUES
    ('region', 'standard', 2020, 15), ('region', 'efficient', 2020, 15);
UPDATE metadata_real SET value = 0.05 WHERE element = 'default_loan_rate';
UPDATE metadata_real SET value = 0.02 WHERE element = 'global_discount_rate';
