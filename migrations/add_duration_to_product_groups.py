"""
Migration to update the product_groups table.
This migration adds duration_id field to the product_groups table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = 'add_duration_to_product_groups'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add duration_id column to the product_groups table
    op.execute(text("""
    ALTER TABLE product_groups 
    ADD COLUMN duration_id INTEGER,
    ADD CONSTRAINT fk_product_groups_duration FOREIGN KEY (duration_id) REFERENCES list_items (id) ON DELETE SET NULL
    """))

def downgrade():
    # Remove the duration_id column from the product_groups table
    op.execute(text("""
    ALTER TABLE product_groups 
    DROP CONSTRAINT fk_product_groups_duration,
    DROP COLUMN duration_id
    """)) 