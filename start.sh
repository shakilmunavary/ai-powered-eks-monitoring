#!/bin/bash

# Create virtual environment if missing
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Flask app in background
nohup python eks.py > flask.log 2>&1 &

echo "Flask app started in background on port 5001. Logs: flask.log"
