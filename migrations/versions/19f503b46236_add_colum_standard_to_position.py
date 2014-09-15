"""add colum standard to position

Revision ID: 19f503b46236
Revises: 2b831b35f37a
Create Date: 2014-09-15 07:39:25.005105

"""

# revision identifiers, used by Alembic.
revision = '19f503b46236'
down_revision = '2b831b35f37a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ad_position', sa.Column('standard', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ad_position', 'standard')
    ### end Alembic commands ###
