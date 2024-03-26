import os
import re
import sys
import ffmpeg
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

OUTPUT_FOLDER = os.environ["BIRDNET_OUTPUT_FOLDER"]
SNIPPETS_FOLDER = f"{OUTPUT_FOLDER}/snippets"
RESULTS_FOLDER = f"{OUTPUT_FOLDER}/results"


def split_mp3(input_file, output_folder, chunk_duration=10 * 60):
    # Get input file name without extension
    input_file_name = os.path.splitext(os.path.basename(input_file))[0]

    # Get duration of input file
    probe = ffmpeg.probe(input_file)

    duration = float(probe['format']['duration'])

    # Calculate number of chunks
    num_chunks = int(duration / chunk_duration) + 1
    print(f"Splitting file into {num_chunks} chunks")
    # Split the file into chunks
    for i in range(num_chunks):
        print(f"Writing chunk {i + 1} of {num_chunks}")
        start_time = i * chunk_duration
        end_time = min((i + 1) * chunk_duration, duration)
        output_file = os.path.join(output_folder, f"{input_file_name}_{i}.mp3")

        ffmpeg.input(input_file, ss=start_time, to=end_time).output(output_file, loglevel="quiet").run(
            overwrite_output=True)


def create_audit_segment(input_file, output_file, start_time, end_time):
    (
        ffmpeg
        .input(input_file, ss=start_time)
        .output(output_file, to=end_time, codec='copy',
                loglevel="quiet")
        .run()
    )


def get_chunk_number_from_file(file_name: str) -> int:
    pattern = r'\d+$'
    match = re.search(pattern, file_name)
    return int(match.group())


def seconds_to_hours_and_minutes(seconds):
    # Calculate hours, remaining minutes, and remaining seconds
    hours = seconds // 3600
    remaining_minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    return hours, remaining_minutes, remaining_seconds


def _append_line_to_file(file_path, line):
    """Append a line to a file."""
    with open(file_path, 'a') as file:
        file.write(line + '\n')


def _append_to_label_track(label_track_file_path: str,
                           start_time: int,
                           end_time: int,
                           species: str,
                           confidence_level: str):
    _append_line_to_file(label_track_file_path,
                         f"{start_time}.0\t{end_time}.0\t{species} ({confidence_level})")


def _create_detection_snippets(detections, input_file_path, label_track_file_path: str):
    original_file_name = os.path.basename(input_file_path)
    original_file_name_without_extension, _ = os.path.splitext(original_file_name)
    chunk_start_seconds = get_chunk_number_from_file(original_file_name_without_extension) * 10 * 60
    print(f"{chunk_start_seconds} chunk start seconds")

    for detection in detections:
        start_time = round(detection['start_time'])
        end_time = round(detection['end_time']) + 1
        overall_time_in_recording_seconds = chunk_start_seconds + start_time
        hours, minutes, seconds = seconds_to_hours_and_minutes(overall_time_in_recording_seconds)
        output_file_name = f"{original_file_name_without_extension}_{hours}_{minutes}_{seconds}_{detection['common_name'].replace(' ', '')}.mp3"
        create_audit_segment(input_file_path, f"{RESULTS_FOLDER}/{output_file_name}", start_time, end_time)
        _append_to_label_track(
            label_track_file_path=label_track_file_path,
            start_time=overall_time_in_recording_seconds,
            end_time=chunk_start_seconds + end_time,
            species=detection['common_name'],
            confidence_level=detection['confidence']
        )


def analyse_file(file_path: str, analyzer, label_track_file_path: str):
    recording = Recording(
        analyzer,
        file_path,
        lat=54.0491,
        lon=-2.7877,
        date=datetime(year=2023, month=3, day=30),  # use date or week_48
        min_conf=0.60,
    )
    recording.analyze()
    print(f"Got results for {file_path}")
    print(recording.detections)
    _create_detection_snippets(recording.detections, file_path, label_track_file_path)
    os.remove(file_path)



def analyse(input_filename: str):
    print(f"Splitting provided file {input_filename} into chunks")
    os.makedirs(SNIPPETS_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    split_mp3(input_filename, SNIPPETS_FOLDER)
    original_file_name_without_extension, _ = os.path.splitext(input_filename)
    label_track_file_path = f"{original_file_name_without_extension}_labels.txt"
    print("Finished splitting, starting analysis")
    analyzer = Analyzer()
    for file in sorted(os.listdir(SNIPPETS_FOLDER)):
        print(f"Analysing {file}")
        analyse_file(f"{SNIPPETS_FOLDER}/{file}", analyzer, label_track_file_path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    input_filename = sys.argv[1]
    analyse(input_filename)
