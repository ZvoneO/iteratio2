import sys
import os
import logging
from sqlalchemy import text

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Project, List, ListItem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_app()

def migrate_project_statuses():
    """
    Migration script to add status_id to projects table and populate it based on existing status values.
    """
    with app.app_context():
        try:
            # Check if the column exists
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('projects')]
            
            if 'status_id' not in columns:
                logger.info("Adding status_id column to projects table...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE projects ADD COLUMN status_id INTEGER REFERENCES list_items(id)'))
                    conn.commit()
                logger.info("Column added successfully.")
            else:
                logger.info("status_id column already exists in projects table.")
            
            # Get the ProjectStatusList
            project_statuses_list = List.query.filter_by(id=6).first()
            if not project_statuses_list:
                logger.error("ProjectStatusList not found. Migration cannot continue.")
                return
            
            # Get all status items
            status_items = ListItem.query.filter_by(list_id=project_statuses_list.id).all()
            status_map = {item.value: item.id for item in status_items}
            
            logger.info(f"Found {len(status_items)} status items: {status_map}")
            
            # Get all projects
            projects = Project.query.all()
            logger.info(f"Found {len(projects)} projects to update.")
            
            # Update each project
            for project in projects:
                if project.status and project.status in status_map:
                    project.status_id = status_map[project.status]
                    logger.info(f"Updated project {project.id} ({project.name}): status '{project.status}' -> status_id {project.status_id}")
                else:
                    # Default to "Preparation" if status not found
                    preparation_id = status_map.get('Preparation')
                    if preparation_id:
                        project.status_id = preparation_id
                        project.status = 'Preparation'
                        logger.info(f"Set default status for project {project.id} ({project.name}): status_id {project.status_id}")
                    else:
                        logger.warning(f"Could not set status for project {project.id} ({project.name}): status '{project.status}' not found in map and no default available.")
            
            # Commit changes
            db.session.commit()
            logger.info("Migration completed successfully.")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_project_statuses() 