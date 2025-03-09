"""
Script to run the client model migration.
"""

from app import create_app, db
from sqlalchemy import text
from migrations.update_client_model import upgrade

def run_migration():
    """
    Run the client model migration.
    """
    app = create_app()
    with app.app_context():
        # Run the migration
        upgrade()
        print("Client model migration completed successfully")

if __name__ == "__main__":
    run_migration() 