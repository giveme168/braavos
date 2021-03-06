"""add colum self_agent_rebate in douban_order

Revision ID: 424b76369e0f
Revises: 4bfb38542cc6
Create Date: 2016-03-09 11:24:37.082473

"""

# revision identifiers, used by Alembic.
revision = '424b76369e0f'
down_revision = '4bfb38542cc6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_douban_order', sa.Column('self_agent_rebate', sa.String(length=20), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_douban_order', 'self_agent_rebate')
    ### end Alembic commands ###
