import os
import re
from datetime import datetime, timezone

import ffmpeg
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

from config import RESULTS_FOLDER
from models import BirdObservation
from observation_storage import store_observation


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

def extract_date_from_filename(file_path):
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', file_path)

    assert match is not None, f"Could not get date from file path {file_path}"
    date_string = match.group(1)
    return datetime.fromisoformat(date_string)


def _create_and_send_detection_snippets(detections, input_file_path):
    original_file_name = os.path.basename(input_file_path)
    original_file_name_without_extension, _ = os.path.splitext(original_file_name)

    for detection in detections:
        start_time = round(detection['start_time'])
        end_time = round(detection['end_time']) + 1
        output_file_name = f"{original_file_name_without_extension}_{detection['common_name'].replace(' ', '')}_{start_time}.mp3"
        full_output_file_path = f"{RESULTS_FOLDER}/{output_file_name}"
        _create_audio_segment(input_file_path, full_output_file_path, start_time, end_time)
        detection_date = extract_date_from_filename(full_output_file_path)
        send_bird_audio_file_to_bluesky(
            detection_data=detection,
            file_path=full_output_file_path,
            detection_time=detection_date
        )

        store_observation(
            BirdObservation(
                common_species_name=detection['common_name'],
                scientific_name=detection['scientific_name'],
                time=detection_date,
                recording_filename=full_output_file_path,
                confidence=str(detection['confidence'])
            )
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
