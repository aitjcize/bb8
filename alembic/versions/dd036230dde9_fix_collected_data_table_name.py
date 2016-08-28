"""fix collected_data table name

Revision ID: dd036230dde9
Revises: c9d6ce4066e5
Create Date: 2016-08-20 07:52:30.260731

"""

# revision identifiers, used by Alembic.
revision = 'dd036230dde9'
down_revision = '420ba26be66b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.rename_table('colleted_data', 'collected_data')


def downgrade():
    op.rename_table('collected_data', 'colleted_data')
