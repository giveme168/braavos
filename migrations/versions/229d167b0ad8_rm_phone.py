"""rm phone

Revision ID: 229d167b0ad8
Revises: 3dc05209d727
Create Date: 2014-12-16 11:42:27.784501

"""

# revision identifiers, used by Alembic.
revision = '229d167b0ad8'
down_revision = '3dc05209d727'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'phone')
    op.drop_constraint(u'user_phone_key', 'user')
    op.drop_index('user_phone_key', table_name='user')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('user_phone_key', 'user', ['phone'], unique=True)
    op.create_unique_constraint(u'user_phone_key', 'user', ['phone'])
    op.add_column('user', sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    ### end Alembic commands ###
