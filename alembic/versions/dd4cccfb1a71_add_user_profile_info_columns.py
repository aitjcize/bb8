"""add user profile info columns

Revision ID: dd4cccfb1a71
Revises: 44a59ee9c0b0
Create Date: 2016-06-23 14:51:29.165175

"""

# revision identifiers, used by Alembic.
revision = 'dd4cccfb1a71'
down_revision = '44a59ee9c0b0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('first_name', sa.Unicode(length=32), nullable=True))
    op.add_column('user', sa.Column('gender', sa.Unicode(length=16), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.Unicode(length=32), nullable=True))
    op.add_column('user', sa.Column('locale', sa.Unicode(length=16), nullable=True))
    op.add_column('user', sa.Column('timezone', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('user', 'timezone')
    op.drop_column('user', 'locale')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'gender')
    op.drop_column('user', 'first_name')
