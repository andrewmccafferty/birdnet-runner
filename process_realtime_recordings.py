import os
import re
from datetime import datetime, timezone

import ffmpeg
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

from config import RESULTS_FOLDER, SCAN_RECORDINGS_FOLDER
from send_slack_data import send_bird_audio_file_to_slack


def _create_audio_segment(input_file, output_file, start_time, end_time):
    try:
        print(f"Writing file {input_file} to {output_file}")
        (ffmpeg
         .input(input_file, ss=start_time)
         .output(output_file, to=end_time, codec='copy', loglevel="quiet")
         .run(overwrite_output=True))
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e


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
    print(f"Got {len(recording.detections)} results for {file_path}")
    _create_and_send_detection_snippets(detections=recording.detections, input_file_path=file_path)
    os.remove(file_path)
    return recording.detections


def extract_hour_from_filename(filename):
    # Define the regular expression pattern to extract the hour
    pattern = r'final_\d{4}-\d{2}-\d{2}T(\d{2})-\d{2}-\d{2}\.mp3'

    # Search for the pattern in the filename
    match = re.search(pattern, filename)

    # Check if a match was found
    if match:
        # Extract the hour part from the match
        hour = match.group(1)
        print(f"Got hour {hour} from filename {filename}")
        return int(hour)
    else:
        return None


def filename_is_within_time_constraint(filename: str) -> bool:
    hour = extract_hour_from_filename(filename)
    return hour >= 22 or hour < 3


def process_recordings_in_scan_folder(folder: str):
    files_to_analyse = sorted([file_name for file_name in os.listdir(folder)
                               if file_name.endswith(".mp3") and filename_is_within_time_constraint(file_name)])
    if len(files_to_analyse) == 0:
        print("No files to analyse")
        return
    print(f"Analysing {len(files_to_analyse)} files...")
    analyzer = Analyzer()
    for file in files_to_analyse:
        print(f"Analysing {file}")
        _analyse_file(f"{folder}/{file}", analyzer)
