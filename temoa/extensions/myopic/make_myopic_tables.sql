BEGIN;

CREATE TABLE IF NOT EXISTS myopic_efficiency
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
-- for efficient searching by rtv:
CREATE INDEX IF NOT EXISTS region_tech_vintage ON myopic_efficiency (region, tech, vintage);


COMMIT;
