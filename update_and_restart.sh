#!/bin/bash

# update_and_restart.sh - Script to update the database and restart the application
# This script runs the database update and restarts the application

echo "Updating database and restarting application..."

# 1. Activate the virtual environment
source venv/bin/activate

# 2. Ensure PYTHONHOME and PYTHONPATH are unset to avoid conflicts
unset PYTHONHOME
unset PYTHONPATH

# 3. Run the database update
echo "Updating database..."
python update_db.py

# 4. Restart the application
echo "Restarting the application..."
sudo systemctl restart iteratio

echo "Update completed and application restarted!"
echo "You can now access the application with the new expertise storage system." 