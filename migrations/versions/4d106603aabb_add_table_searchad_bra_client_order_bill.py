"""add table searchad_bra_client_order_bill

Revision ID: 4d106603aabb
Revises: 1ac203a35b62
Create Date: 2016-06-29 11:10:06.752328

"""

# revision identifiers, used by Alembic.
revision = '4d106603aabb'
down_revision = '1ac203a35b62'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('searchad_bra_client_order_bill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company', sa.String(length=100), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('medium_id', sa.Integer(), nullable=True),
    sa.Column('resource_type', sa.Integer(), nullable=True),
    sa.Column('money', sa.Float(), nullable=True),
    sa.Column('rebate_money', sa.Float(), nullable=True),
    sa.Column('start', sa.Date(), nullable=True),
    sa.Column('end', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['searchAd_client.id'], ),
    sa.ForeignKeyConstraint(['medium_id'], ['searchAd_medium.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('searchad_bra_client_order_bill')
    ### end Alembic commands ###