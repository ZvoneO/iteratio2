import sys
import os
import logging
from sqlalchemy import text

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_app()

def migrate_phase_status():
    """
    Migration script to add status column to project_phases table.
    """
    with app.app_context():
        try:
            # Check if the column exists
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('project_phases')]
            
            if 'status' not in columns:
                logger.info("Adding status column to project_phases table...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE project_phases ADD COLUMN status VARCHAR(20) DEFAULT 'Not Started'"))
                    conn.commit()
                logger.info("Column added successfully.")
            else:
                logger.info("status column already exists in project_phases table.")
            
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_phase_status() 