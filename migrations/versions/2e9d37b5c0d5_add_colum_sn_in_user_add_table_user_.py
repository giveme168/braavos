"""add colum sn in user add table user_onduty

Revision ID: 2e9d37b5c0d5
Revises: 4848d1d9da29
Create Date: 2015-12-04 16:57:38.441686

"""

# revision identifiers, used by Alembic.
revision = '2e9d37b5c0d5'
down_revision = '4848d1d9da29'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_onduty',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('sn', sa.String(length=10), nullable=True),
    sa.Column('check_time', sa.DateTime(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sn', 'check_time', name='_user_onduty_sn_check_time')
    )
    op.create_index(op.f('ix_user_onduty_check_time'), 'user_onduty', ['check_time'], unique=False)
    op.create_index(op.f('ix_user_onduty_create_time'), 'user_onduty', ['create_time'], unique=False)
    op.create_index(op.f('ix_user_onduty_sn'), 'user_onduty', ['sn'], unique=False)
    op.add_column(u'user', sa.Column('sn', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_user_sn'), 'user', ['sn'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_sn'), table_name='user')
    op.drop_column(u'user', 'sn')
    op.drop_index(op.f('ix_user_onduty_sn'), table_name='user_onduty')
    op.drop_index(op.f('ix_user_onduty_create_time'), table_name='user_onduty')
    op.drop_index(op.f('ix_user_onduty_check_time'), table_name='user_onduty')
    op.drop_table('user_onduty')
    ### end Alembic commands ###
