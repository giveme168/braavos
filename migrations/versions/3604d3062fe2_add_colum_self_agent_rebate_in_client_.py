"""add colum self_agent_rebate in client_order

Revision ID: 3604d3062fe2
Revises: 15d76c9fb0f1
Create Date: 2016-01-26 11:27:12.698092

"""

# revision identifiers, used by Alembic.
revision = '3604d3062fe2'
down_revision = '15d76c9fb0f1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_client_order', sa.Column('self_agent_rebate', sa.String(length=20), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_client_order', 'self_agent_rebate')
    ### end Alembic commands ###
