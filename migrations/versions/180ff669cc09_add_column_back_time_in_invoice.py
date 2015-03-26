"""add column back_time in invoice

Revision ID: 180ff669cc09
Revises: 1fbb54143a8e
Create Date: 2015-03-26 13:57:49.440276

"""

# revision identifiers, used by Alembic.
revision = '180ff669cc09'
down_revision = '1fbb54143a8e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bra_invoice', sa.Column('back_time', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bra_invoice', 'back_time')
    ### end Alembic commands ###
