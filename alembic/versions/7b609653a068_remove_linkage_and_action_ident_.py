"""remove linkage and action_ident indirection

Revision ID: 7b609653a068
Revises: 248e43bdefd0
Create Date: 2016-10-08 16:38:56.196640

"""

# revision identifiers, used by Alembic.
revision = '7b609653a068'
down_revision = '248e43bdefd0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_table('linkage')
    op.drop_column('bot', 'start_node_id')
    op.drop_column('bot', 'root_node_id')
    op.add_column('node', sa.Column('stable_id', sa.String(length=128), nullable=False))
    op.create_unique_constraint(None, 'node', ['bot_id', 'stable_id'])


def downgrade():
    op.drop_constraint(None, 'node', type_='unique')
    op.drop_column('node', 'stable_id')
    op.add_column('bot', sa.Column('root_node_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('bot', sa.Column('start_node_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_table('linkage',
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('bot_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('start_node_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('end_node_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('action_ident', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=128), nullable=False),
    sa.Column('ack_message', sa.BLOB(), nullable=False),
    sa.ForeignKeyConstraint(['bot_id'], [u'bot.id'], name=u'linkage_ibfk_1'),
    sa.ForeignKeyConstraint(['end_node_id'], [u'node.id'], name=u'linkage_ibfk_3'),
    sa.ForeignKeyConstraint(['start_node_id'], [u'node.id'], name=u'linkage_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
