"""add colum performance_user

Revision ID: 2a438435c68e
Revises: 233a80382122
Create Date: 2015-08-26 14:49:01.053771

"""

# revision identifiers, used by Alembic.
revision = '2a438435c68e'
down_revision = '233a80382122'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('performance_user', sa.Column('performance_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('performance_user', 'performance_id')
    ### end Alembic commands ###
