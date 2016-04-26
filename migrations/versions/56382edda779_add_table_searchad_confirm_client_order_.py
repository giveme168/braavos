"""add table searchad_confirm_client_order_money

Revision ID: 56382edda779
Revises: 1ee54c609d14
Create Date: 2016-04-12 12:38:41.792598

"""

# revision identifiers, used by Alembic.
revision = '56382edda779'
down_revision = '1ee54c609d14'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('searchad_bra_client_order_confirm_money',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_order_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('money', sa.Float(), nullable=True),
    sa.Column('rebate', sa.Float(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('Q', sa.String(length=2), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['client_order_id'], ['searchAd_bra_client_order.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['searchAd_bra_order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('searchad_bra_client_order_confirm_money')
    ### end Alembic commands ###