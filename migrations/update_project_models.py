"""
Migration to update the projects table and add project groups and phases.
This migration adds industry_id and profit_center_id to the projects table,
and creates project_groups and project_phases tables.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = 'update_project_models'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to the projects table
    op.execute(text("""
    ALTER TABLE projects 
    ADD COLUMN industry_id INTEGER REFERENCES list_items(id),
    ADD COLUMN profit_center_id INTEGER REFERENCES list_items(id)
    """))
    
    # Create project_groups table
    op.execute(text("""
    CREATE TABLE project_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        product_group_id INTEGER NOT NULL,
        order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (product_group_id) REFERENCES product_groups(id)
    )
    """))
    
    # Create project_phases table
    op.execute(text("""
    CREATE TABLE project_phases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        duration_id INTEGER,
        online BOOLEAN DEFAULT 0,
        order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES project_groups(id) ON DELETE CASCADE,
        FOREIGN KEY (duration_id) REFERENCES list_items(id)
    )
    """))

def downgrade():
    # Drop the project_phases table
    op.execute(text("DROP TABLE IF EXISTS project_phases"))
    
    # Drop the project_groups table
    op.execute(text("DROP TABLE IF EXISTS project_groups"))
    
    # Remove the new columns from the projects table
    op.execute(text("""
    ALTER TABLE projects 
    DROP COLUMN industry_id,
    DROP COLUMN profit_center_id
    """)) 