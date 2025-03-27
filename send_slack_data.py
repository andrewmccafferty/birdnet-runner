import datetime
import os
import re
import requests
from typing import Optional

from slack_sdk import WebClient
from prettytable import PrettyTable
from config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, NO_SLACK_SEND, EXCLUDED_SPECIES, SPECIES_COUNTS_SLACK_CHANNEL_ID, BLUESKY_APP_PASSWORD, BLUESKY_HANDLE
from models import SightingReport
from datetime import timezone, time

session_data: Optional[dict] = None

def get_bsky_new_session() -> dict:
    global session_data
    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
    )
    print(f"Response from BlueSky {resp.json()}")
    resp.raise_for_status()
    session_data = resp.json()
    return session_data

def bsky_login_session() -> dict:
    global session_data
    if not session_data:
        session_data = get_bsky_new_session()
        return session_data
    return session_data  


def is_nocmig_time():
    now = datetime.datetime.now().time()
    start_time = time(19, 30)
    end_time = time(4, 0)
    return now >= start_time or now < end_time

def send_bluesky_message_with_token(post, session):
    now = datetime.datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    resp = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": post,
                "createdAt": now
            }
        },
    )
    print(f"Response from BlueSky {resp.json()}")
    return resp

def send_bluesky_message(post):
    session = bsky_login_session()
    resp = send_bluesky_message_with_token(post, session)
    if resp.status_code == 400:
        session = get_bsky_new_session()
        resp = send_bluesky_message_with_token(post, session)
    resp.raise_for_status()

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
    if not is_nocmig_time():
        return
    try:
        send_bluesky_message(f"🐦 {species} detected at {detection_time} 🐦")
    except Exception as exception:
        print(f"Got error while using BlueSky: {exception}") 
    # client.files_upload_v2(
    #     channel=SLACK_CHANNEL_ID,
    #     title=os.path.basename(file_path),
    #     file=file_path,
    #     initial_comment=f"🐦 {species} detected at {detection_time} 🐦",
    # )


def send_species_aggregate_report_to_slack(reports: list[SightingReport]):
    if NO_SLACK_SEND:
        print(f"Slack notifications off, not sending species report")
        return
    client = WebClient(SLACK_BOT_TOKEN)
    table = PrettyTable()
    table.field_names = ["Species", "Last heard"]
    table.add_rows([[report.species_name, report.last_hearing] for report in reports])
    print("Sending message")
    try:
        send_bluesky_message(f"{table}")
    except Exception as exception:
        print(f"Got error while using BlueSky: {exception}") 
    # message_response = client.chat_postMessage(
    #     channel=SPECIES_COUNTS_SLACK_CHANNEL_ID,
    #     text=f"```{table}```"
    # )
    # for report in reports:
    #     print(f"Uploading file {report.last_hearing_filename}")
    #     # client.files_upload_v2(
    #     #     channel=SPECIES_COUNTS_SLACK_CHANNEL_ID,
    #     #     thread_ts=message_response["ts"],
    #     #     title=os.path.basename(report.last_hearing_filename),
    #     #     file=report.last_hearing_filename,
    #     #     initial_comment=f"🐦 {report.species_name} last detected at {report.last_hearing} 🐦",
    #     # )

if __name__ == '__main__':
    send_species_aggregate_report_to_slack([
        SightingReport(
            species_name="Blackbird",
            last_hearing=datetime.datetime.utcnow(),
            last_hearing_filename="/Users/andrewmccafferty/Documents/personal/birds/nocmig/realtime_results/results/final_2024-07-21T11-46-00_EurasianMagpie_3.mp3"
        ),
        SightingReport(
            species_name="Bluethroat (just kidding)",
            last_hearing=datetime.datetime.utcnow(),
            last_hearing_filename="/Users/andrewmccafferty/Documents/personal/birds/nocmig/realtime_results/results/final_2024-07-21T11-45-00_EuropeanGoldfinch_27.mp3"
        )
    ])