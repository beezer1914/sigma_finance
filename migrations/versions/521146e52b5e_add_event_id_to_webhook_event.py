"""add_event_id_to_webhook_event

Revision ID: 521146e52b5e
Revises: 234a07669603
Create Date: 2025-10-20 15:23:35.203773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '521146e52b5e'
down_revision = '234a07669603'
branch_labels = None
depends_on = None


def upgrade():
    # Add event_id column to webhook_event table
    op.add_column('webhook_event', sa.Column('event_id', sa.String(length=128), nullable=True))

    # Add unique constraint and index on event_id
    op.create_index(op.f('ix_webhook_event_event_id'), 'webhook_event', ['event_id'], unique=True)


def downgrade():
    # Remove index and column
    op.drop_index(op.f('ix_webhook_event_event_id'), table_name='webhook_event')
    op.drop_column('webhook_event', 'event_id')
