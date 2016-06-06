"""add column order_id in IntertionOrder

Revision ID: 56e4b905ebac
Revises: f4407b14bef
Create Date: 2016-04-25 15:37:15.738824

"""

# revision identifiers, used by Alembic.
revision = '56e4b905ebac'
down_revision = 'f4407b14bef'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_intention_order', sa.Column('order_id', sa.String(length=10), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_intention_order', 'order_id')
    ### end Alembic commands ###