"""add colum bank in finance pay

Revision ID: 6209c388432
Revises: 1064cb14cbf3
Create Date: 2016-07-25 15:46:02.630921

"""

# revision identifiers, used by Alembic.
revision = '6209c388432'
down_revision = '1064cb14cbf3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_agent_invoice_pay', sa.Column('bank', sa.String(length=100), nullable=True))
    op.add_column('bra_agent_invoice_pay', sa.Column('bank_num', sa.String(length=100), nullable=True))
    op.add_column('bra_agent_invoice_pay', sa.Column('company', sa.String(length=100), nullable=True))
    op.add_column('bra_medium_invoice_pay', sa.Column('bank', sa.String(length=100), nullable=True))
    op.add_column('bra_medium_invoice_pay', sa.Column('bank_num', sa.String(length=100), nullable=True))
    op.add_column('bra_medium_invoice_pay', sa.Column('company', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_medium_invoice_pay', 'company')
    op.drop_column('bra_medium_invoice_pay', 'bank_num')
    op.drop_column('bra_medium_invoice_pay', 'bank')
    op.drop_column('bra_agent_invoice_pay', 'company')
    op.drop_column('bra_agent_invoice_pay', 'bank_num')
    op.drop_column('bra_agent_invoice_pay', 'bank')
    ### end Alembic commands ###