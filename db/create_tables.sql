
create table sighting(id serial PRIMARY KEY, common_species_name varchar, scientific_name varchar, time timestamp, stored_time timestamp, recording_filename varchar);

CREATE USER birdnet_runner WITH PASSWORD 'CHANGEME';
GRANT SELECT ON TABLE sighting TO birdnet_runner;
GRANT INSERT ON TABLE sighting TO birdnet_runner;
GRANT USAGE, SELECT ON SEQUENCE sighting_id_seq TO birdnet_runner;