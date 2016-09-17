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

import pickle

import sqlalchemy as sa

from alembic import op
from sqlalchemy.sql import table, column


def upgrade():
    op.add_column('user', sa.Column('memory', sa.PickleType(), nullable=True))
    op.add_column('user', sa.Column('settings', sa.PickleType(), nullable=True))
    user = table('user', column('memory'), column('settings'))
    try:
        op.execute(user.update().values(memory=pickle.dumps({})))
        op.execute(user.update().values(settings=pickle.dumps({})))
    except: pass
    op.alter_column('user', 'memory', nullable=False)
    op.alter_column('user', 'settings', nullable=False)



def downgrade():
    op.drop_column('user', 'settings')
    op.drop_column('user', 'memory')
