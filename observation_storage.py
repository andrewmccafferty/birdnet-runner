import datetime

import psycopg2

from config import SIGHTINGS_DB_NAME, SIGHTINGS_DB_USER, SIGHTINGS_DB_PASSWORD, SIGHTINGS_DB_HOST
from models import BirdObservation, SightingReport


def get_db_connection():
    return psycopg2.connect(f"host={SIGHTINGS_DB_HOST} "
        f"dbname={SIGHTINGS_DB_NAME} "
                            f"user={SIGHTINGS_DB_USER} "
                            f"password={SIGHTINGS_DB_PASSWORD}")


def upsert_species(conn, common_species_name, scientific_name):
    # Define the upsert SQL statement
    upsert_sql = """
    INSERT INTO species (common_species_name, scientific_name)
    VALUES (%s, %s)
    ON CONFLICT (scientific_name)
    DO UPDATE SET common_species_name = EXCLUDED.common_species_name
    RETURNING id;
    """

    try:
        with conn.cursor() as cur:
            # Execute the upsert query
            cur.execute(upsert_sql, (common_species_name, scientific_name))

            # Fetch the result
            result = cur.fetchone()
            if result:
                species_id = result[0]
            else:
                # This should not happen, but just in case
                raise Exception("Upsert operation did not return an ID")

            # Commit the transaction
            conn.commit()

            return species_id
    except Exception as e:
        conn.rollback()
        raise e

def store_observation(observation: BirdObservation):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        species_id = upsert_species(
            conn,
            common_species_name=observation.common_species_name,
            scientific_name=observation.scientific_name)
        cur.execute("INSERT INTO sighting("
                    "species_id, "
                    "time, "
                    "stored_time, "
                    "confidence, "
                    "recording_filename) "
                    "VALUES(%s, %s, %s, %s, %s)",
                    (species_id,
                     observation.time,
                     datetime.datetime.now(tz=datetime.timezone.utc),
                     observation.confidence,
                     observation.recording_filename))
        conn.commit()
    except Exception as exc:
        print(f"Got error {exc} while trying to store observation")
    finally:
        conn.close()


def get_species_counts() -> list[SightingReport]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = """
        WITH LastSighting AS (
            SELECT 
                s.common_species_name, 
                max(sg.time) as last_hearing
            FROM 
                sighting sg 
            JOIN 
                species s ON s.id = sg.species_id 
            WHERE 
                sg.time > now()::date 
            GROUP BY 
                s.common_species_name
        )
        SELECT 
            s.common_species_name,
            ls.last_hearing,
            max(sg.recording_filename)
        FROM 
            LastSighting ls
        JOIN
            species s ON s.common_species_name = ls.common_species_name 
        JOIN 
            sighting sg ON sg.time = ls.last_hearing
            AND sg.species_id = s.id 
        GROUP BY s.common_species_name, ls.last_hearing
        ORDER BY 
            s.common_species_name;
        """

        cur.execute(query)
        results = cur.fetchall()
        reports = [SightingReport(
            species_name=row[0],
            last_hearing=row[1],
            last_hearing_filename=row[2]
        ) for row in results]
        return reports
    except Exception as exc:
        print(f"Got error while getting species counts {exc}")
        return []
    finally:
        conn.close()


if __name__ == '__main__':
    # In the absence of tests, here's a quick and dirty
    # check that the data storage works
    store_observation(BirdObservation(
        common_species_name="Dunnock",
        scientific_name="Prunella modularis",
        time=datetime.datetime.fromisoformat("2024-07-29 09:20:52.691037"),
        recording_filename="Some_filename.mp3",
        confidence=0.60
    ))
    counts = get_species_counts()
    print(counts)
