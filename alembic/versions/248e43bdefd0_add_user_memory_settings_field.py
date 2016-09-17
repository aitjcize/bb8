"""add user memory/settings field

Revision ID: 248e43bdefd0
Revises: b08fa78fbb27
Create Date: 2016-09-17 18:10:54.304843

"""

# revision identifiers, used by Alembic.
revision = '248e43bdefd0'
down_revision = 'b08fa78fbb27'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('memory', sa.PickleType(), nullable=False))
    op.add_column('user', sa.Column('settings', sa.PickleType(), nullable=False))


def downgrade():
    op.drop_column('user', 'settings')
    op.drop_column('user', 'memory')
