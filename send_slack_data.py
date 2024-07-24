import datetime
import os
import re

from slack_sdk import WebClient

from config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, NO_SLACK_SEND, EXCLUDED_SPECIES, SPECIES_COUNTS_SLACK_CHANNEL_ID
from models import SightingReport


def _should_send_species_notification(species: str) -> bool:
    return species not in EXCLUDED_SPECIES

def send_bird_audio_file_to_slack(
        detection_data: dict,
        file_path: str,
        detection_time: datetime.datetime):
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
        initial_comment=f"🐦 {species} detected at {detection_time} 🐦",
    )

def send_species_aggregate_report_to_slack(reports: list[SightingReport]):
    if NO_SLACK_SEND:
        print(f"Slack notifications off, not sending species report")
        return
    client = WebClient(SLACK_BOT_TOKEN)
    species_rows = "\n".join([
        f"{report.species_name}, {report.last_hearing}, {report.today_count}" for report in reports
    ])
    client.chat_postMessage(
        channel=SPECIES_COUNTS_SLACK_CHANNEL_ID,
        text="species name, last hearing, count today\n\n"
        f"{species_rows}"
    )

if __name__ == '__main__':
    send_species_aggregate_report_to_slack([
        SightingReport(
            species_name="Blackbird",
            last_hearing=datetime.datetime.utcnow(),
            today_count=5
        ),
        SightingReport(
            species_name="Bluethroat (just kidding)",
            last_hearing=datetime.datetime.utcnow(),
            today_count=5
        )
    ])