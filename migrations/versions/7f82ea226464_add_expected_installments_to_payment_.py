"""Add expected_installments to payment_plan

Revision ID: 7f82ea226464
Revises: 621f3c79083a
Create Date: 2025-09-06 10:56:01.883093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f82ea226464'
down_revision = '621f3c79083a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('payment_plan', sa.Column('expected_installments', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('payment_plan', 'expected_installments')

