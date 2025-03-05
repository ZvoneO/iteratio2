"""Initial migration

Revision ID: f0aab1235443
Revises: 
Create Date: 2025-03-05 11:55:10.920791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0aab1235443'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('expertise_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('product_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('consultants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('surname', sa.String(length=50), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('availability_days_per_month', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('calendar_name', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('list_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products_services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['product_groups.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('country_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['country_id'], ['list_items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('consultant_expertise',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('consultant_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['expertise_categories.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['consultant_id'], ['consultants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('phase_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('duration_days', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['project_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('template_id', sa.Integer(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['project_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('template_products',
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products_services.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['template_id'], ['project_templates.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('template_id', 'product_id')
    )
    op.create_table('project_products',
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products_services.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('project_id', 'product_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project_products')
    op.drop_table('template_products')
    op.drop_table('projects')
    op.drop_table('phase_templates')
    op.drop_table('project_templates')
    op.drop_table('consultant_expertise')
    op.drop_table('clients')
    op.drop_table('products_services')
    op.drop_table('list_items')
    op.drop_table('consultants')
    op.drop_table('users')
    op.drop_table('product_groups')
    op.drop_table('lists')
    op.drop_table('expertise_categories')
    # ### end Alembic commands ###
