"""add colum mediums incase

Revision ID: 47f5c5f9d5d9
Revises: 42533addb511
Create Date: 2015-09-24 17:18:37.636293

"""

# revision identifiers, used by Alembic.
revision = '47f5c5f9d5d9'
down_revision = '42533addb511'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('case_mediums',
    sa.Column('medium_id', sa.Integer(), nullable=True),
    sa.Column('case_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['case_id'], ['bra_case.id'], ),
    sa.ForeignKeyConstraint(['medium_id'], ['medium.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('case_mediums')
    ### end Alembic commands ###