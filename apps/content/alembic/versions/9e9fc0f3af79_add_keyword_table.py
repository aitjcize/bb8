"""add keyword table

Revision ID: 9e9fc0f3af79
Revises:
Create Date: 2016-08-28 16:50:56.051543

"""

# revision identifiers, used by Alembic.
revision = '9e9fc0f3af79'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('keyword',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.Unicode(length=64), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['keyword.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('keyword')
