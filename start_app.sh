#!/bin/bash

# start_app.sh - Script to start the application with the fixed environment
# This script ensures the database is properly migrated and roles are set up

echo "Starting application setup..."

# 1. Activate virtual environment
source venv/bin/activate

# 2. Ensure PYTHONHOME and PYTHONPATH are unset to avoid conflicts
unset PYTHONHOME
unset PYTHONPATH

# 3. Run database migrations
echo "Running database migrations..."
flask db upgrade

# 4. Run the data migration script to set up roles
echo "Setting up roles..."
python scripts/data_migration.py

# 5. Start the application with a different port if 5000 is in use
echo "Starting the application..."
# Check if port 5000 is in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 5000 is already in use. Using port 5001 instead."
    export FLASK_RUN_PORT=5001
    python run.py
else
    python run.py
fi

echo "Application started!" 