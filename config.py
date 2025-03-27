import os

SCAN_RECORDINGS_FOLDER = os.environ["SCAN_RECORDINGS_FOLDER"]
OUTPUT_FOLDER = os.environ["OUTPUT_FOLDER"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
SPECIES_COUNTS_SLACK_CHANNEL_ID = os.environ["SPECIES_COUNTS_SLACK_CHANNEL_ID"]

BLUESKY_HANDLE = os.environ["BLUESKY_HANDLE"]
BLUESKY_APP_PASSWORD = os.environ["BLUESKY_APP_PASSWORD"]
SNIPPETS_FOLDER = f"{OUTPUT_FOLDER}/snippets"
RESULTS_FOLDER = f"{OUTPUT_FOLDER}/results"

NO_SLACK_SEND = True if os.environ.get("NO_SLACK_SEND") == "1" else False
SIGHTINGS_DB_HOST = os.environ["SIGHTINGS_DB_HOST"]
SIGHTINGS_DB_NAME = os.environ["SIGHTINGS_DB_NAME"]
SIGHTINGS_DB_USER = os.environ["SIGHTINGS_DB_USER"]
SIGHTINGS_DB_PASSWORD = os.environ["SIGHTINGS_DB_PASSWORD"]


def _generate_excluded_species_list() -> list[str]:
    configured_list_csv = os.environ.get("EXCLUDED_SPECIES")
    if not configured_list_csv:
        return []

    return configured_list_csv.split(",")


EXCLUDED_SPECIES = _generate_excluded_species_list()
