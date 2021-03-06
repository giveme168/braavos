"""douban add resource type

Revision ID: 3f0b1b1b898
Revises: 5427463a333f
Create Date: 2015-01-13 18:07:28.846164

"""

# revision identifiers, used by Alembic.
revision = '3f0b1b1b898'
down_revision = '5427463a333f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_douban_order', sa.Column('resource_type', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_douban_order', 'resource_type')
    ### end Alembic commands ###
