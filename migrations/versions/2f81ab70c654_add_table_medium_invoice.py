"""add table medium_invoice

Revision ID: 2f81ab70c654
Revises: 180ff669cc09
Create Date: 2015-03-27 11:40:34.705720

"""

# revision identifiers, used by Alembic.
revision = '2f81ab70c654'
down_revision = '180ff669cc09'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bra_medium_invoice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_order_id', sa.Integer(), nullable=True),
    sa.Column('medium_id', sa.Integer(), nullable=True),
    sa.Column('company', sa.String(length=100), nullable=True),
    sa.Column('tax_id', sa.String(length=100), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=80), nullable=True),
    sa.Column('bank_id', sa.String(length=20), nullable=True),
    sa.Column('bank', sa.String(length=100), nullable=True),
    sa.Column('detail', sa.String(length=200), nullable=True),
    sa.Column('money', sa.Float(), nullable=True),
    sa.Column('invoice_type', sa.Integer(), nullable=True),
    sa.Column('invoice_status', sa.Integer(), nullable=True),
    sa.Column('invoice_num', sa.String(length=200), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.Column('pay_time', sa.DateTime(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('bool_pay', sa.Boolean(), nullable=True),
    sa.Column('bool_invoice', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['client_order_id'], ['bra_client_order.id'], ),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['medium_id'], ['medium.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bra_medium_invoice')
    ### end Alembic commands ###
