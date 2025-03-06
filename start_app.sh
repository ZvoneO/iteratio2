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

# 5. Start the application
echo "Starting the application..."
python run.py

echo "Application started!" 