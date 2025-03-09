"""
Script to add missing columns to the clients table.
"""

from app import create_app, db
from sqlalchemy import text

def add_columns():
    """
    Add sales_person and project_manager columns to the clients table.
    """
    app = create_app()
    with app.app_context():
        # Check if columns already exist
        try:
            # Try to select from the columns to see if they exist
            db.session.execute(text("SELECT sales_person, project_manager FROM clients LIMIT 1"))
            print("Columns already exist.")
            return
        except Exception:
            # Columns don't exist, add them
            try:
                db.session.execute(text("ALTER TABLE clients ADD COLUMN sales_person VARCHAR(100)"))
                db.session.execute(text("ALTER TABLE clients ADD COLUMN project_manager VARCHAR(100)"))
                db.session.commit()
                print("Columns added successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding columns: {str(e)}")

if __name__ == "__main__":
    add_columns() 