"""add colum abbreviation

Revision ID: 4738e8321b11
Revises: 20756762ccf1
Create Date: 2014-12-17 15:10:42.585725

"""

# revision identifiers, used by Alembic.
revision = '4738e8321b11'
down_revision = '20756762ccf1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medium', sa.Column('abbreviation', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('medium', 'abbreviation')
    ### end Alembic commands ###
