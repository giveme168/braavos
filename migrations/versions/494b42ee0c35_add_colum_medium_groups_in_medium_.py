"""add colum medium_groups in medium_framework_order

Revision ID: 494b42ee0c35
Revises: 40501173f0b8
Create Date: 2016-08-08 10:42:28.541408

"""

# revision identifiers, used by Alembic.
revision = '494b42ee0c35'
down_revision = '40501173f0b8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medium_framework_order_medium_groups',
    sa.Column('medium_group_id', sa.Integer(), nullable=True),
    sa.Column('medium_group_framework_order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['medium_group_framework_order_id'], ['bra_medium_framework_order.id'], ),
    sa.ForeignKeyConstraint(['medium_group_id'], ['medium_group.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medium_framework_order_medium_groups')
    ### end Alembic commands ###
