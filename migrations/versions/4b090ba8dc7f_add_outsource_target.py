"""add outsource target

Revision ID: 4b090ba8dc7f
Revises: 2ac75a48af33
Create Date: 2015-01-29 15:26:25.006372

"""

# revision identifiers, used by Alembic.
revision = '4b090ba8dc7f'
down_revision = '2ac75a48af33'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('out_source_target',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('bank', sa.String(length=100), nullable=True),
    sa.Column('card', sa.String(length=100), nullable=True),
    sa.Column('alipay', sa.String(length=100), nullable=True),
    sa.Column('contract', sa.String(length=1000), nullable=True),
    sa.Column('remark', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('out_source_target')
    ### end Alembic commands ###
