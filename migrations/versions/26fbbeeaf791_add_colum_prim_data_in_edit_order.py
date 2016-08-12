"""add colum prim_data in edit order

Revision ID: 26fbbeeaf791
Revises: 28d5ea8eaef0
Create Date: 2016-08-12 15:10:27.799530

"""

# revision identifiers, used by Alembic.
revision = '26fbbeeaf791'
down_revision = '28d5ea8eaef0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_edit_client_order', sa.Column('prim_client_order_data', sa.Text(), nullable=True))
    op.add_column('bra_edit_order', sa.Column('prim_order_data', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_edit_order', 'prim_order_data')
    op.drop_column('bra_edit_client_order', 'prim_client_order_data')
    ### end Alembic commands ###
