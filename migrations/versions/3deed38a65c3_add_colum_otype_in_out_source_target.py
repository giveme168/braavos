"""add colum otype in out_source_target

Revision ID: 3deed38a65c3
Revises: 42d521195c39
Create Date: 2015-06-03 17:06:55.058798

"""

# revision identifiers, used by Alembic.
revision = '3deed38a65c3'
down_revision = '42d521195c39'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('out_source_target', sa.Column('otype', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('out_source_target', 'otype')
    ### end Alembic commands ###
