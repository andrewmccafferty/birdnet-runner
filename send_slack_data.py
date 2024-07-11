import os

from slack_sdk import WebClient

from config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID


def send_bird_audio_file_to_slack(
        detection_data: dict,
        file_path: str):
    client = WebClient(SLACK_BOT_TOKEN)
    species = detection_data['common_name']

    client.files_upload_v2(
        channel=SLACK_CHANNEL_ID,
        title=os.path.basename(file_path),
        file=file_path,
        initial_comment=f"🐦 Possible {species} detected 🐦",
    )