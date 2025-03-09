#!/bin/bash

# create_table_direct.sh - Script to create the expertise table directly using sqlite3
# This script creates the expertise table and restarts the application

echo "Creating expertise table and restarting application..."

# 1. Find the database file
DB_FILE="instance/app.db"
if [ ! -f "$DB_FILE" ]; then
    echo "Database file not found at $DB_FILE"
    exit 1
fi

# 2. Run the SQL commands directly
echo "Creating expertise table..."
sqlite3 "$DB_FILE" < create_table.sql

# 3. Restart the application
echo "Restarting the application..."
sudo systemctl restart iteratio

echo "Table creation completed and application restarted!"
echo "You can now access the application with the new expertise storage system." 