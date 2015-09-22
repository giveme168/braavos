"""add table personal outsource

Revision ID: 50ad8e409732
Revises: 5810fb3e73e5
Create Date: 2015-09-14 16:01:01.355297

"""

# revision identifiers, used by Alembic.
revision = '50ad8e409732'
down_revision = '5810fb3e73e5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('merger_douban_personal_out_source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice', sa.Boolean(), nullable=True),
    sa.Column('pay_num', sa.Float(), nullable=True),
    sa.Column('num', sa.Float(), nullable=True),
    sa.Column('remark', sa.String(length=1000), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('merger_personal_out_source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice', sa.Boolean(), nullable=True),
    sa.Column('pay_num', sa.Float(), nullable=True),
    sa.Column('num', sa.Float(), nullable=True),
    sa.Column('remark', sa.String(length=1000), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('merger_personal_out_source')
    op.drop_table('merger_douban_personal_out_source')
    ### end Alembic commands ###