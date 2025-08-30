"""Add created_at to invite_code"""

from alembic import op
import sqlalchemy as sa

revision = '1416718e9d54'
down_revision = '5e30e0c904e6'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('invite_code') as batch_op:
        batch_op.add_column(
            sa.Column(
                'created_at',
                sa.DateTime(),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=False
            )
        )

def downgrade():
    with op.batch_alter_table('invite_code') as batch_op:
        batch_op.drop_column('created_at')