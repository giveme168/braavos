"""add index

Revision ID: d0322c4ef81
Revises: 394466a4f1c8
Create Date: 2015-12-29 15:09:45.966062

"""

# revision identifiers, used by Alembic.
revision = 'd0322c4ef81'
down_revision = '394466a4f1c8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_bra_client_order_executive_report_client_order_id'), 'bra_client_order_executive_report', ['client_order_id'], unique=False)
    op.create_index(op.f('ix_bra_client_order_executive_report_month_day'), 'bra_client_order_executive_report', ['month_day'], unique=False)
    op.create_index(op.f('ix_bra_medium_order_executive_report_client_order_id'), 'bra_medium_order_executive_report', ['client_order_id'], unique=False)
    op.create_index(op.f('ix_bra_medium_order_executive_report_month_day'), 'bra_medium_order_executive_report', ['month_day'], unique=False)
    op.create_index(op.f('ix_bra_medium_order_executive_report_order_id'), 'bra_medium_order_executive_report', ['order_id'], unique=False)
    op.create_index(op.f('ix_bra_outsource_executive_report_month_day'), 'bra_outsource_executive_report', ['month_day'], unique=False)
    op.create_index(op.f('ix_bra_outsource_executive_report_otype'), 'bra_outsource_executive_report', ['otype'], unique=False)
    op.create_index(op.f('ix_bra_outsource_executive_report_outsource_id'), 'bra_outsource_executive_report', ['outsource_id'], unique=False)
    op.create_index(op.f('ix_bra_outsource_executive_report_type'), 'bra_outsource_executive_report', ['type'], unique=False)
    op.create_index(op.f('ix_douban_out_source_douban_order_id'), 'douban_out_source', ['douban_order_id'], unique=False)
    op.create_index(op.f('ix_out_source_medium_order_id'), 'out_source', ['medium_order_id'], unique=False)
    op.create_index(op.f('ix_user_leave_create_time'), 'user_leave', ['create_time'], unique=False)
    op.create_index(op.f('ix_user_leave_end_time'), 'user_leave', ['end_time'], unique=False)
    op.create_index(op.f('ix_user_leave_start_time'), 'user_leave', ['start_time'], unique=False)
    op.create_index(op.f('ix_user_out_create_time'), 'user_out', ['create_time'], unique=False)
    op.create_index(op.f('ix_user_out_end_time'), 'user_out', ['end_time'], unique=False)
    op.create_index(op.f('ix_user_out_start_time'), 'user_out', ['start_time'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_out_start_time'), table_name='user_out')
    op.drop_index(op.f('ix_user_out_end_time'), table_name='user_out')
    op.drop_index(op.f('ix_user_out_create_time'), table_name='user_out')
    op.drop_index(op.f('ix_user_leave_start_time'), table_name='user_leave')
    op.drop_index(op.f('ix_user_leave_end_time'), table_name='user_leave')
    op.drop_index(op.f('ix_user_leave_create_time'), table_name='user_leave')
    op.drop_index(op.f('ix_out_source_medium_order_id'), table_name='out_source')
    op.drop_index(op.f('ix_douban_out_source_douban_order_id'), table_name='douban_out_source')
    op.drop_index(op.f('ix_bra_outsource_executive_report_type'), table_name='bra_outsource_executive_report')
    op.drop_index(op.f('ix_bra_outsource_executive_report_outsource_id'), table_name='bra_outsource_executive_report')
    op.drop_index(op.f('ix_bra_outsource_executive_report_otype'), table_name='bra_outsource_executive_report')
    op.drop_index(op.f('ix_bra_outsource_executive_report_month_day'), table_name='bra_outsource_executive_report')
    op.drop_index(op.f('ix_bra_medium_order_executive_report_order_id'), table_name='bra_medium_order_executive_report')
    op.drop_index(op.f('ix_bra_medium_order_executive_report_month_day'), table_name='bra_medium_order_executive_report')
    op.drop_index(op.f('ix_bra_medium_order_executive_report_client_order_id'), table_name='bra_medium_order_executive_report')
    op.drop_index(op.f('ix_bra_client_order_executive_report_month_day'), table_name='bra_client_order_executive_report')
    op.drop_index(op.f('ix_bra_client_order_executive_report_client_order_id'), table_name='bra_client_order_executive_report')
    ### end Alembic commands ###