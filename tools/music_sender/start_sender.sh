#!/bin/bash
# start_sender.sh - Bash script to run music_sender.py

echo "Starting ArcadeMatrix Music Sender..."
echo

python3 "$(dirname "$0")/music_sender.py" --port 8085

echo
echo "Music sender stopped."