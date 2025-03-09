"""
Script to create the consultant_expertise table.
This script creates the consultant_expertise table without migrating any data.
"""

from app import create_app, db
from sqlalchemy import text
import logging
import sys
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_expertise_table():
    """
    Create the consultant_expertise table without migrating any data.
    """
    try:
        logger.info("Starting application context...")
        app = create_app()
        with app.app_context():
            try:
                conn = db.engine.connect()
                
                # Create a new table with the updated schema
                logger.info("Creating new consultant_expertise table...")
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS consultant_expertise_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consultant_id INTEGER NOT NULL,
                    product_group_id INTEGER,
                    product_element_id INTEGER,
                    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    notes TEXT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (consultant_id) REFERENCES consultants (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_group_id) REFERENCES product_groups (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_element_id) REFERENCES product_elements (id) ON DELETE CASCADE
                )
                """))
                
                # Drop the existing table if it exists
                logger.info("Dropping old consultant_expertise table...")
                conn.execute(text("DROP TABLE IF EXISTS consultant_expertise"))
                
                # Rename the new table to the original name
                logger.info("Renaming new table to consultant_expertise...")
                conn.execute(text("ALTER TABLE consultant_expertise_new RENAME TO consultant_expertise"))
                
                # Commit the schema changes
                conn.commit()
                logger.info("Consultant expertise table created successfully")
            except Exception as e:
                logger.error(f"Error creating table: {str(e)}")
                logger.error(traceback.format_exc())
                raise
    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    try:
        logger.info("Starting table creation process...")
        create_expertise_table()
        logger.info("Table creation process completed successfully")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1) 