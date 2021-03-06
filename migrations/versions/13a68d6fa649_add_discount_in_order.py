"""add discount in order

Revision ID: 13a68d6fa649
Revises: 4724e30f478b
Create Date: 2014-10-09 10:26:32.244756

"""

# revision identifiers, used by Alembic.
revision = '13a68d6fa649'
down_revision = '4724e30f478b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_order', sa.Column('discount', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_order', 'discount')
    ### end Alembic commands ###
