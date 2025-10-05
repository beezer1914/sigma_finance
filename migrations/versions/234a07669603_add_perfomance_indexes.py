"""add_perfomance_indexes

Revision ID: 234a07669603
Revises: 8a5a34d89c28
Create Date: 2025-10-05 18:50:03.853674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234a07669603'
down_revision = '8a5a34d89c28'
branch_labels = None
depends_on = None


def upgrade():
    # User table indexes
    op.create_index('ix_user_email_lower', 'user', [sa.text('LOWER(email)')], unique=True)
    op.create_index('ix_user_role', 'user', ['role'])
    op.create_index('ix_user_active', 'user', ['active'])
    op.create_index('ix_user_financial_status', 'user', ['financial_status'])
    
    # Payment table indexes - CRITICAL for performance
    op.create_index('ix_payment_user_id_date', 'payment', ['user_id', 'date'])
    op.create_index('ix_payment_plan_id', 'payment', ['plan_id'])
    op.create_index('ix_payment_date', 'payment', ['date'])
    op.create_index('ix_payment_method', 'payment', ['method'])
    op.create_index('ix_payment_type', 'payment', ['payment_type'])
    
    # PaymentPlan table indexes
    op.create_index('ix_payment_plan_user_status', 'payment_plan', ['user_id', 'status'])
    op.create_index('ix_payment_plan_status', 'payment_plan', ['status'])
    op.create_index('ix_payment_plan_start_date', 'payment_plan', ['start_date'])
    op.create_index('ix_payment_plan_end_date', 'payment_plan', ['end_date'])
    
    # InviteCode table indexes
    op.create_index('ix_invite_code_code', 'invite_code', ['code'])
    op.create_index('ix_invite_code_used', 'invite_code', ['used'])
    op.create_index('ix_invite_code_expires_at', 'invite_code', ['expires_at'])
    
    # WebhookEvent table indexes
    op.create_index('ix_webhook_event_type', 'webhook_event', ['event_type'])
    op.create_index('ix_webhook_processed', 'webhook_event', ['processed'])
    op.create_index('ix_webhook_received_at', 'webhook_event', ['received_at'])
    op.create_index('ix_webhook_type_processed', 'webhook_event', ['event_type', 'processed'])


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('ix_webhook_type_processed', 'webhook_event')
    op.drop_index('ix_webhook_received_at', 'webhook_event')
    op.drop_index('ix_webhook_processed', 'webhook_event')
    op.drop_index('ix_webhook_event_type', 'webhook_event')
    
    op.drop_index('ix_invite_code_expires_at', 'invite_code')
    op.drop_index('ix_invite_code_used', 'invite_code')
    op.drop_index('ix_invite_code_code', 'invite_code')
    
    op.drop_index('ix_payment_plan_end_date', 'payment_plan')
    op.drop_index('ix_payment_plan_start_date', 'payment_plan')
    op.drop_index('ix_payment_plan_status', 'payment_plan')
    op.drop_index('ix_payment_plan_user_status', 'payment_plan')
    
    op.drop_index('ix_payment_type', 'payment')
    op.drop_index('ix_payment_method', 'payment')
    op.drop_index('ix_payment_date', 'payment')
    op.drop_index('ix_payment_plan_id', 'payment')
    op.drop_index('ix_payment_user_id_date', 'payment')
    
    op.drop_index('ix_user_financial_status', 'user')
    op.drop_index('ix_user_active', 'user')
    op.drop_index('ix_user_role', 'user')
    op.drop_index('ix_user_email_lower', 'user')
