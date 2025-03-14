"""Remove duplicated fields from consultants table

Revision ID: 00df300402e2
Revises: d68705152fbf
Create Date: 2025-03-07 09:10:17.818170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00df300402e2'
down_revision = 'd68705152fbf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consultants', schema=None) as batch_op:
        batch_op.drop_column('name')
        batch_op.drop_column('full_name')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('email')
        batch_op.drop_column('surname')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consultants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('surname', sa.VARCHAR(length=50), nullable=False))
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=120), nullable=True))
        batch_op.add_column(sa.Column('phone_number', sa.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('full_name', sa.VARCHAR(length=100), nullable=False))
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=50), nullable=False))

    # ### end Alembic commands ###
