"""add admin_interaction_timeout and admin_last_seen

Revision ID: c9d6ce4066e5
Revises: 973d410b7648
Create Date: 2016-08-05 14:46:45.129507

"""

# revision identifiers, used by Alembic.
revision = 'c9d6ce4066e5'
down_revision = '973d410b7648'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('bot', sa.Column('admin_interaction_timeout', sa.Integer(),
                  nullable=False))
    op.add_column('user', sa.Column('last_admin_seen', sa.DateTime(),
                  nullable=False))


def downgrade():
    op.drop_column('user', 'last_admin_seen')
    op.drop_column('bot', 'admin_interaction_timeout')
