"""add bot.ga_id field

Revision ID: b08fa78fbb27
Revises: dd036230dde9
Create Date: 2016-09-11 07:19:59.564697

"""

# revision identifiers, used by Alembic.
revision = 'b08fa78fbb27'
down_revision = 'dd036230dde9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('bot', sa.Column('ga_id', sa.Unicode(length=32), nullable=True))


def downgrade():
    op.drop_column('bot', 'ga_id')
