#!/bin/bash
PID=$(ps aux | grep '[p]ython eks.py' | awk '{print $2}')
if [ -n "$PID" ]; then
  kill $PID
  echo "Flask app (PID $PID) stopped."
else
  echo "No running Flask app found."
fi
