import os
import re

from slack_sdk import WebClient

from config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, NO_SLACK_SEND, EXCLUDED_SPECIES


def extract_date_from_filename(file_path):
    # Define the regex pattern to match the ISO timestamp in the file name
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})'

    # Search for the pattern in the file path
    match = re.search(pattern, file_path)

    # If a match is found, return the timestamp with colons instead of hyphens for time parts
    if match:
        iso_timestamp = match.group(1).replace('-', ':', 2)
        return iso_timestamp
    else:
        return None

def _should_send_species_notification(species: str) -> bool:
    return species not in EXCLUDED_SPECIES

def send_bird_audio_file_to_slack(
        detection_data: dict,
        file_path: str):
    client = WebClient(SLACK_BOT_TOKEN)
    species = detection_data['common_name']

    if NO_SLACK_SEND:
        print(f"Slack notifications off, skipping Slack send of {species}")
        return

    if not _should_send_species_notification(species):
        print(f"Skipping Slack send of {species} because it's excluded from notifications")
        return

    client.files_upload_v2(
        channel=SLACK_CHANNEL_ID,
        title=os.path.basename(file_path),
        file=file_path,
        initial_comment=f"🐦 {species} detected at {extract_date_from_filename(file_path)} 🐦",
    )