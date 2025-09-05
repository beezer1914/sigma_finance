"""Merge multiple heads after migration cleanup

Revision ID: 621f3c79083a
Revises: 1416718e9d54, 85d7fb485cfb
Create Date: 2025-09-05 16:07:35.735717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '621f3c79083a'
down_revision = ('1416718e9d54', '85d7fb485cfb')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
