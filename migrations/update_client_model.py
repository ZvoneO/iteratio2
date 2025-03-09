"""
Migration to update the clients table.
This migration adds sales_person and project_manager fields to the clients table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = 'update_client_model'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to the clients table
    op.execute(text("""
    ALTER TABLE clients 
    ADD COLUMN sales_person VARCHAR(100),
    ADD COLUMN project_manager VARCHAR(100)
    """))

def downgrade():
    # Remove the new columns from the clients table
    op.execute(text("""
    ALTER TABLE clients 
    DROP COLUMN sales_person,
    DROP COLUMN project_manager
    """)) 