"""make ack message pickle type

Revision ID: 973d410b7648
Revises: 3d72a1c7c90f
Create Date: 2016-06-28 14:50:46.767666

"""

# revision identifiers, used by Alembic.
revision = '973d410b7648'
down_revision = '3d72a1c7c90f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.alter_column('linkage', 'ack_message',
               existing_type=mysql.TEXT(collation=u'utf8_unicode_ci'),
               type_=sa.PickleType(),
               existing_nullable=False)


def downgrade():
    op.alter_column('linkage', 'ack_message',
               existing_type=sa.PickleType(),
               type_=mysql.TEXT(collation=u'utf8_unicode_ci'),
               existing_nullable=False)
