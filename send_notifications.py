import datetime
import requests
from typing import Optional

from config import BLUESKY_APP_PASSWORD, BLUESKY_HANDLE

from datetime import timezone, time

from dawn_dusk_calculator import is_between_dusk_and_dawn

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

def send_bird_audio_file_to_bluesky(
        detection_data: dict,
        file_path: str,
        detection_time: datetime.datetime):
    species = detection_data['common_name']
    if not is_between_dusk_and_dawn():
        print("Not sending notification because it isn't night time")
        return
    try:
        send_bluesky_message(f"🐦 {species} detected at {detection_time} 🐦")
    except Exception as exception:
        print(f"Got error while using BlueSky: {exception}")