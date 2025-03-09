#!/bin/bash

# run_migrations.sh - Script to run the database migrations and restart the application
# This script runs the database migrations and restarts the application

echo "Running database migrations..."

# 1. Activate the virtual environment
source venv/bin/activate

# 2. Ensure PYTHONHOME and PYTHONPATH are unset to avoid conflicts
unset PYTHONHOME
unset PYTHONPATH

# 3. Create a simple migration script to run the update
cat > run_migration.py << 'EOF'
from app import create_app, db
from sqlalchemy import text
from migrations.update_consultant_expertise import upgrade

app = create_app()
with app.app_context():
    # Run the migration
    upgrade()
    print("Database schema updated successfully")
EOF

# 4. Run the database schema update
echo "Updating database schema..."
python run_migration.py

# 5. Migrate the expertise data
echo "Migrating expertise data..."
python migrations/migrate_expertise_data.py

# 6. Restart the application
echo "Restarting the application..."
sudo systemctl restart iteratio

# 7. Clean up temporary files
rm run_migration.py

echo "Migration completed and application restarted!"
echo "You can now access the application with the new expertise storage system." 