CREATE USER birdnet_runner WITH PASSWORD 'CHANGEME';

CREATE TABLE species
(
    id                  serial PRIMARY KEY,
    common_species_name varchar,
    scientific_name     varchar UNIQUE
);

CREATE TABLE sighting
(
    id                 serial PRIMARY KEY,
    species_id         serial,
    time               timestamp,
    stored_time        timestamp,
    recording_filename varchar,
    confidence numeric,
    CONSTRAINT fk_species
        FOREIGN KEY (species_id)
            REFERENCES species (id)
);

GRANT SELECT ON TABLE sighting TO birdnet_runner;
GRANT INSERT ON TABLE sighting TO birdnet_runner;
GRANT SELECT ON TABLE species to birdnet_runner;
GRANT UPDATE ON TABLE species to birdnet_runner;
GRANT INSERT ON TABLE species to birdnet_runner;
GRANT USAGE, SELECT ON SEQUENCE sighting_id_seq TO birdnet_runner;
GRANT USAGE, SELECT ON SEQUENCE species_id_seq to birdnet_runner;