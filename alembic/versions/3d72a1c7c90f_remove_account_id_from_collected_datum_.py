"""remove account_id from collected_datum table

Revision ID: 3d72a1c7c90f
Revises: dd4cccfb1a71
Create Date: 2016-06-25 08:51:15.331321

"""

# revision identifiers, used by Alembic.
revision = '3d72a1c7c90f'
down_revision = 'dd4cccfb1a71'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_constraint(u'colleted_data_ibfk_1', 'colleted_data', type_='foreignkey')
    op.drop_column('colleted_data', 'account_id')


def downgrade():
    op.add_column('colleted_data', sa.Column('account_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.create_foreign_key(u'colleted_data_ibfk_1', 'colleted_data', 'account', ['account_id'], ['id'])
