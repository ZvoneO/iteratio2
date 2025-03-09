"""
Script to add project-related tables and columns to the database.
"""

from app import create_app, db
from sqlalchemy import text

def add_tables_and_columns():
    """
    Add project-related tables and columns to the database.
    """
    app = create_app()
    with app.app_context():
        # Add new columns to the projects table
        try:
            # Check if columns already exist
            db.session.execute(text("SELECT industry_id, profit_center_id FROM projects LIMIT 1"))
            print("Project columns already exist.")
        except Exception:
            # Add columns
            try:
                db.session.execute(text("ALTER TABLE projects ADD COLUMN industry_id INTEGER REFERENCES list_items(id)"))
                db.session.execute(text("ALTER TABLE projects ADD COLUMN profit_center_id INTEGER REFERENCES list_items(id)"))
                db.session.commit()
                print("Project columns added successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding project columns: {str(e)}")
        
        # Create project_groups table
        try:
            # Check if table already exists
            db.session.execute(text("SELECT * FROM project_groups LIMIT 1"))
            print("Project groups table already exists.")
        except Exception:
            # Create table
            try:
                db.session.execute(text("""
                CREATE TABLE project_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    product_group_id INTEGER NOT NULL,
                    "order" INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_group_id) REFERENCES product_groups(id)
                )
                """))
                db.session.commit()
                print("Project groups table created successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating project groups table: {str(e)}")
        
        # Create project_phases table
        try:
            # Check if table already exists
            db.session.execute(text("SELECT * FROM project_phases LIMIT 1"))
            print("Project phases table already exists.")
        except Exception:
            # Create table
            try:
                db.session.execute(text("""
                CREATE TABLE project_phases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    duration_id INTEGER,
                    online BOOLEAN DEFAULT 0,
                    "order" INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES project_groups(id) ON DELETE CASCADE,
                    FOREIGN KEY (duration_id) REFERENCES list_items(id)
                )
                """))
                db.session.commit()
                print("Project phases table created successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating project phases table: {str(e)}")

if __name__ == "__main__":
    add_tables_and_columns() 