"""add colum framework

Revision ID: 3f8b6443b09a
Revises: 143bade867cc
Create Date: 2014-12-18 18:25:18.384209

"""

# revision identifiers, used by Alembic.
revision = '3f8b6443b09a'
down_revision = '143bade867cc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medium', sa.Column('framework', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('medium', 'framework')
    ### end Alembic commands ###
