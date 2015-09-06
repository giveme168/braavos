"""add colum replace in order

Revision ID: 2e4ec4661d34
Revises: 325177319c0f
Create Date: 2015-09-06 14:27:27.878458

"""

# revision identifiers, used by Alembic.
revision = '2e4ec4661d34'
down_revision = '325177319c0f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('douban_order_replace_sales',
    sa.Column('replace_sale_id', sa.Integer(), nullable=True),
    sa.Column('douban_order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['douban_order_id'], ['bra_douban_order.id'], ),
    sa.ForeignKeyConstraint(['replace_sale_id'], ['user.id'], )
    )
    op.create_table('client_order_replace_sales',
    sa.Column('replace_sale_id', sa.Integer(), nullable=True),
    sa.Column('client_order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_order_id'], ['bra_client_order.id'], ),
    sa.ForeignKeyConstraint(['replace_sale_id'], ['user.id'], )
    )
    op.add_column(u'bra_order', sa.Column('finish_status', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'bra_order', 'finish_status')
    op.drop_table('client_order_replace_sales')
    op.drop_table('douban_order_replace_sales')
    ### end Alembic commands ###
