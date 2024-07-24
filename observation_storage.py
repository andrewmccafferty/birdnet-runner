import datetime

import psycopg2

from config import SIGHTINGS_DB_NAME, SIGHTINGS_DB_USER, SIGHTINGS_DB_PASSWORD
from models import BirdObservation


def get_db_connection():
    return psycopg2.connect(f"dbname={SIGHTINGS_DB_NAME} "
                            f"user={SIGHTINGS_DB_USER} "
                            f"password={SIGHTINGS_DB_PASSWORD}")


def store_observation(observation: BirdObservation):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO sighting("
                    "common_species_name, "
                    "scientific_name, "
                    "time, "
                    "stored_time, "
                    "recording_filename) "
                    "VALUES(%s, %s, %s, %s, %s)",
                    (observation.common_species_name,
                     observation.scientific_name,
                     observation.time,
                     datetime.datetime.now(tz=datetime.timezone.utc),
                     observation.recording_filename))
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    # In the absence of tests, here's a quick and dirty
    # check that the data storage works
    store_observation(BirdObservation(
        common_species_name="Blackbird",
        scientific_name="Turdus Merula",
        time=datetime.datetime.now(),
        recording_filename="Some_filename.mp3"
    ))
