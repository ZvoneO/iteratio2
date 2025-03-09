"""
Migration to update the consultant_expertise table.
This migration modifies the consultant_expertise table to ensure only meaningful expertise is stored.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = 'update_consultant_expertise'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table with the updated schema
    op.create_table(
        'consultant_expertise_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('consultant_id', sa.Integer, nullable=False),
        sa.Column('product_group_id', sa.Integer, nullable=True),
        sa.Column('product_element_id', sa.Integer, nullable=True),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['consultant_id'], ['consultants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_group_id'], ['product_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_element_id'], ['product_elements.id'], ondelete='CASCADE'),
        sa.CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating_range')
    )
    
    # Drop the existing table if it exists
    conn = op.get_bind()
    conn.execute(text("DROP TABLE IF EXISTS consultant_expertise"))
    
    # Rename the new table to the original name
    op.rename_table('consultant_expertise_new', 'consultant_expertise')

def downgrade():
    # Drop the new table
    op.drop_table('consultant_expertise')
    
    # Recreate the original table
    op.create_table(
        'consultant_expertise',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('consultant_id', sa.Integer, nullable=False),
        sa.Column('category_id', sa.Integer, nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.ForeignKeyConstraint(['category_id'], ['expertise_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['consultant_id'], ['consultants.id'], ondelete='CASCADE')
    ) 