import os
from datetime import datetime, timezone

import ffmpeg
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

from config import RESULTS_FOLDER, SCAN_RECORDINGS_FOLDER
from send_slack_data import send_bird_audio_file_to_slack


def _create_audio_segment(input_file, output_file, start_time, end_time):
    (
        ffmpeg
        .input(input_file, ss=start_time)
        .output(output_file, to=end_time, codec='copy',
                loglevel="quiet")
        .run(overwrite_output=True)
    )


def _create_and_send_detection_snippets(detections, input_file_path):
    original_file_name = os.path.basename(input_file_path)
    original_file_name_without_extension, _ = os.path.splitext(original_file_name)

    for detection in detections:
        start_time = round(detection['start_time'])
        end_time = round(detection['end_time']) + 1
        output_file_name = f"{original_file_name_without_extension}_{detection['common_name'].replace(' ', '')}_{start_time}.mp3"
        full_output_file_path = f"{RESULTS_FOLDER}/{output_file_name}"
        _create_audio_segment(input_file_path, full_output_file_path, start_time, end_time)
        send_bird_audio_file_to_slack(
            detection_data=detection,
            file_path=full_output_file_path
        )


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
    _create_and_send_detection_snippets(detections=recording.detections, input_file_path=file_path)
    os.remove(file_path)
    return recording.detections


def process_recordings_in_scan_folder(folder: str):
    files_to_analyse = sorted([file_name for file_name in os.listdir(folder)
                               if file_name.endswith(".mp3")])
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
