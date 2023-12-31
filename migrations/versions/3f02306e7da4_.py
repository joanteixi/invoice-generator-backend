"""empty message

Revision ID: 3f02306e7da4
Revises: 
Create Date: 2023-12-31 01:23:03.074906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f02306e7da4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('concept_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'concepts', ['concept_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('concept_id')

    # ### end Alembic commands ###
