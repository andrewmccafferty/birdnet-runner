import os

import schedule
import time

from config import SCAN_RECORDINGS_FOLDER
from copy_data import transfer_and_cleanup_files
from process_realtime_recordings import process_recordings_in_scan_folder

LOCAL_IDENTITY_FILE = os.environ["LOCAL_IDENTITY_FILE"]
REMOTE_USER = os.environ["REMOTE_USER"]
REMOTE_HOST = os.environ["REMOTE_HOST"]
REMOTE_DIRECTORY = os.environ["REMOTE_DIRECTORY"]
LOCAL_DIRECTORY = os.environ["LOCAL_DIRECTORY"]

def run_process():
    try:
        print("Checking for data from Pi")

        transfer_and_cleanup_files(
            LOCAL_IDENTITY_FILE, REMOTE_USER, REMOTE_HOST,
            REMOTE_DIRECTORY, LOCAL_DIRECTORY
        )
        process_recordings_in_scan_folder(SCAN_RECORDINGS_FOLDER)
    except Exception as exception:
        print(f"Got error {exception}")


run_process()
print("Starting timer to get data from Pi every 30 seconds")
schedule.every(30).seconds.do(run_process)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)