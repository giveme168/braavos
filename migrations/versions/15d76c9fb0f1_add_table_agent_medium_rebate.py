"""add table agent_medium_rebate

Revision ID: 15d76c9fb0f1
Revises: 17f176b26fd8
Create Date: 2016-01-22 15:51:38.525049

"""

# revision identifiers, used by Alembic.
revision = '15d76c9fb0f1'
down_revision = '17f176b26fd8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bra_agent_medium_rebate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('medium_id', sa.Integer(), nullable=True),
    sa.Column('rebate', sa.Float(), nullable=True),
    sa.Column('year', sa.Date(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agent.id'], ),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['medium_id'], ['medium.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('agent_id', 'medium_id', 'year', name='_agent_medium_rebate_year')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bra_agent_medium_rebate')
    ### end Alembic commands ###
