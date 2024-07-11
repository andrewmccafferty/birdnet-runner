import json
import os
from datetime import datetime, timezone

import ffmpeg
import requests
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

from config import RESULTS_FOLDER, SCAN_RECORDINGS_FOLDER, NOCMIG_SLACK_WEBHOOK_URL


def _send_slack_message(message: str):
    print(f"Sending Slack message {message} to {NOCMIG_SLACK_WEBHOOK_URL}")
    response = requests.post(
        NOCMIG_SLACK_WEBHOOK_URL,
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "text": message
        }))
    print(f"Finished sending Slack message, response code {response.status_code}, "
          f"response text {response.text}")


def _format_slack_message_for_detection(detection: dict) -> str:
    return f"{detection['common_name']}"


def _send_notifications(recording: Recording, file_path: str):
    species_list = str.join("\n\n",
                            [_format_slack_message_for_detection(detection)
                             for detection in recording.detections])
    _send_slack_message(f"🐦🐦🐦 {file_path}:\n\n {species_list}")


def _create_audit_segment(input_file, output_file, start_time, end_time):
    (
        ffmpeg
        .input(input_file, ss=start_time)
        .output(output_file, to=end_time, codec='copy',
                loglevel="quiet")
        .run(overwrite_output=True)
    )


def _create_detection_snippets(detections, input_file_path):
    original_file_name = os.path.basename(input_file_path)
    original_file_name_without_extension, _ = os.path.splitext(original_file_name)

    for detection in detections:
        start_time = round(detection['start_time'])
        end_time = round(detection['end_time']) + 1
        output_file_name = f"{original_file_name_without_extension}_{detection['common_name'].replace(' ', '')}_{start_time}.mp3"
        _create_audit_segment(input_file_path, f"{RESULTS_FOLDER}/{output_file_name}", start_time, end_time)


def _analyse_file(
        file_path: str, analyzer
) -> dict:
    recording = Recording(
        analyzer,
        file_path,
        lat=54.0491,
        lon=-2.7877,
        date=datetime.now(timezone.utc),  # use date or week_48
        min_conf=0.60,
    )
    recording.analyze()
    print(f"Got results for {file_path}")
    _create_detection_snippets(detections=recording.detections, input_file_path=file_path)
    _send_notifications(recording, os.path.basename(file_path))
    os.remove(file_path)
    return recording.detections


def process_recordings_in_scan_folder(folder: str):
    files_to_analyse = sorted(os.listdir(folder))
    if len(files_to_analyse) == 0:
        print("No files to analyse")
        return
    print(f"Analysing {len(files_to_analyse)} files...")
    analyzer = Analyzer()
    for file in files_to_analyse:
        print(f"Analysing {file}")
        _analyse_file(f"{folder}/{file}", analyzer)


if __name__ == '__main__':
    process_recordings_in_scan_folder(SCAN_RECORDINGS_FOLDER)
