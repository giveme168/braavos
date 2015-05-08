"""add mail record

Revision ID: 1c69f11458de
Revises: 2ca1656e9a54
Create Date: 2015-05-07 22:35:41.146830

"""

# revision identifiers, used by Alembic.
revision = '1c69f11458de'
down_revision = '2ca1656e9a54'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mail',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipients', sa.String(length=1000), nullable=True),
    sa.Column('subject', sa.String(length=1000), nullable=True),
    sa.Column('body', sa.String(length=1000), nullable=True),
    sa.Column('files', sa.String(length=1000), nullable=True),
    sa.Column('remark', sa.String(length=1000), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mail')
    ### end Alembic commands ###
