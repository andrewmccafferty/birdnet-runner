import os

SCAN_RECORDINGS_FOLDER = os.environ["SCAN_RECORDINGS_FOLDER"]
OUTPUT_FOLDER = os.environ["OUTPUT_FOLDER"]

BLUESKY_HANDLE = os.environ["BLUESKY_HANDLE"]
BLUESKY_APP_PASSWORD = os.environ["BLUESKY_APP_PASSWORD"]
SNIPPETS_FOLDER = f"{OUTPUT_FOLDER}/snippets"
RESULTS_FOLDER = f"{OUTPUT_FOLDER}/results"

SIGHTINGS_DB_HOST = os.environ["SIGHTINGS_DB_HOST"]
SIGHTINGS_DB_NAME = os.environ["SIGHTINGS_DB_NAME"]
SIGHTINGS_DB_USER = os.environ["SIGHTINGS_DB_USER"]
SIGHTINGS_DB_PASSWORD = os.environ["SIGHTINGS_DB_PASSWORD"]

LATITUDE = os.environ["LATITUDE"]
LONGITUDE = os.environ["LONGITUDE"]

def _generate_excluded_species_list() -> list[str]:
    configured_list_csv = os.environ.get("EXCLUDED_SPECIES")
    if not configured_list_csv:
        return []

    return configured_list_csv.split(",")


EXCLUDED_SPECIES = _generate_excluded_species_list()
