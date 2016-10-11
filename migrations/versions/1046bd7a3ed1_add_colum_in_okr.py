"""add colum in okr

Revision ID: 1046bd7a3ed1
Revises: adf1d898998
Create Date: 2016-10-10 16:39:18.371497

"""

# revision identifiers, used by Alembic.
revision = '1046bd7a3ed1'
down_revision = 'adf1d898998'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('searchad_bra_client_order_bill', 'invoice_apply_sum')
    op.drop_column('searchad_bra_client_order_bill', 'invoice_pass_sum')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('searchad_bra_client_order_bill', sa.Column('invoice_pass_sum', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('searchad_bra_client_order_bill', sa.Column('invoice_apply_sum', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    ### end Alembic commands ###