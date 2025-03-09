#!/bin/bash

# create_table_and_restart.sh - Script to create the expertise table and restart the application
# This script creates the expertise table and restarts the application

echo "Creating expertise table and restarting application..."

# 1. Run the fix_python_env.sh script to ensure the environment is set up correctly
echo "Setting up Python environment..."
source ./fix_python_env.sh

# 2. Run the table creation script
echo "Creating expertise table..."
source venv/bin/activate
unset PYTHONHOME
unset PYTHONPATH
python3 create_expertise_table.py

# 3. Restart the application
echo "Restarting the application..."
sudo systemctl restart iteratio

echo "Table creation completed and application restarted!"
echo "You can now access the application with the new expertise storage system." 