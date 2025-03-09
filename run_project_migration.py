"""
Script to run the project models migration.
"""

from app import create_app, db
from sqlalchemy import text
from migrations.update_project_models import upgrade

def run_migration():
    """
    Run the project models migration.
    """
    app = create_app()
    with app.app_context():
        # Run the migration
        upgrade()
        print("Project models migration completed successfully")

if __name__ == "__main__":
    run_migration() 