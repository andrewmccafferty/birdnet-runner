#!/bin/bash
FILE_NAME=$(date +"%Y-%m-%dT%H:%M:%S").mp3
OUTPUT_DIR=/path/to/output
echo "Recording sound to ${FILE_NAME}" | systemd-cat
ffmpeg -f alsa -i plughw:1 -t 30 ${OUTPUT_DIR}/temp_${FILE_NAME}
mv ${OUTPUT_DIR}/temp_${FILE_NAME} ${OUTPUT_DIR}/final_${FILE_NAME}