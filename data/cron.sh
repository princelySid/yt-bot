#!/bin/bash

VENV_PYTHON="/path/to/virtual/environment/bin/activate"
PROJECT="/path/to/yt-bot"
PY_FILE="data/tweet_videos.py"
LOG_FILE="path/to/log/tweet.log"

source "$VENV_PYTHON" && cd "$PROJECT" && python "$PY_FILE" >> "$LOG_FILE" 2>&1
