#!/usr/bin/env python3
"""
Script to run the migration to add the duration_id column to the product_groups table.
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Add the current directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def run_migration():
    """Run the migration to add the duration_id column to the product_groups table."""
    try:
        # Create an application context
        with app.app_context():
            # Check if the column already exists
            result = db.session.execute(text("PRAGMA table_info(product_groups)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'duration_id' in columns:
                print("Column 'duration_id' already exists in the product_groups table.")
                return
            
            # Add the duration_id column
            db.session.execute(text("""
            ALTER TABLE product_groups 
            ADD COLUMN duration_id INTEGER
            """))
            
            # Add the foreign key constraint
            db.session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS fk_product_groups_duration
            BEFORE INSERT ON product_groups
            FOR EACH ROW BEGIN
                SELECT CASE
                    WHEN NEW.duration_id IS NOT NULL AND
                         (SELECT id FROM list_items WHERE id = NEW.duration_id) IS NULL
                    THEN RAISE(ABORT, 'Foreign key constraint failed')
                END;
            END;
            """))
            
            db.session.commit()
            print("Migration completed successfully.")
    except Exception as e:
        print(f"Error running migration: {str(e)}")
        try:
            with app.app_context():
                db.session.rollback()
        except Exception:
            pass

if __name__ == '__main__':
    run_migration() 