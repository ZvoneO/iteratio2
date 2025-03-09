#!/bin/bash

# restart_app.sh - Script to restart the application without using sudo
# This script restarts the application by running it directly

echo "Restarting application..."

# 1. Activate the virtual environment
source venv/bin/activate

# 2. Ensure PYTHONHOME and PYTHONPATH are unset to avoid conflicts
unset PYTHONHOME
unset PYTHONPATH

# 3. Kill any existing Python processes running the application
pkill -f "python3 run.py" || true

# 4. Start the application in the background
nohup python3 run.py > app.log 2>&1 &

echo "Application restarted!"
echo "You can now access the application with the updated code." 