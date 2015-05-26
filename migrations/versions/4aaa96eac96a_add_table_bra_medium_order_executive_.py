"""add table bra_medium_order_executive_report

Revision ID: 4aaa96eac96a
Revises: 55b1a1fb7f8e
Create Date: 2015-05-26 11:00:19.387766

"""

# revision identifiers, used by Alembic.
revision = '4aaa96eac96a'
down_revision = '55b1a1fb7f8e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bra_medium_order_executive_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_order_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('medium_money', sa.Float(), nullable=True),
    sa.Column('medium_money2', sa.Float(), nullable=True),
    sa.Column('sale_money', sa.Float(), nullable=True),
    sa.Column('month_day', sa.DateTime(), nullable=True),
    sa.Column('days', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['client_order_id'], ['bra_client_order.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['bra_order.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('client_order_id', 'order_id', 'month_day', name='_medium_order_month_day')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bra_medium_order_executive_report')
    ### end Alembic commands ###
