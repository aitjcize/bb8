"""backend api changes

Revision ID: a4a08467bfb4
Revises: a88f6010bc53
Create Date: 2016-10-15 07:10:09.613683

"""

# revision identifiers, used by Alembic.
revision = 'a4a08467bfb4'
down_revision = 'a88f6010bc53'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('bot_def',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bot_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('bot_json', sa.PickleType(), nullable=False),
    sa.Column('note', sa.Unicode(length=64), nullable=True),
    sa.ForeignKeyConstraint(['bot_id'], ['bot.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('bot_id', 'version')
    )
    op.drop_table('account_bot')
    op.add_column('account', sa.Column('timezone', sa.String(length=32), nullable=False))
    op.create_unique_constraint(None, 'account', ['email'])
    op.add_column('bot', sa.Column('account_id', sa.Integer(), nullable=True))
    op.add_column('bot', sa.Column('staging', sa.PickleType(), nullable=True))
    op.create_foreign_key(None, 'bot', 'account', ['account_id'], ['id'])
    op.add_column('broadcast', sa.Column('account_id', sa.Integer(), nullable=False))
    op.add_column('broadcast', sa.Column('bot_id', sa.Integer(), nullable=False))
    op.add_column('broadcast', sa.Column('messages', sa.PickleType(), nullable=False))
    op.add_column('broadcast', sa.Column('name', sa.Unicode(length=64), nullable=False))
    op.add_column('broadcast', sa.Column('status', sa.Enum('CANCELED', 'QUEUED', 'SENDING', 'SENT', name='broadcaststatusenum'), nullable=False))
    op.alter_column('broadcast', 'scheduled_time',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.create_foreign_key(None, 'broadcast', 'bot', ['bot_id'], ['id'])
    op.create_foreign_key(None, 'broadcast', 'account', ['account_id'], ['id'])
    op.drop_column('broadcast', 'message')
    op.add_column('platform', sa.Column('account_id', sa.Integer(), nullable=True))
    op.add_column('platform', sa.Column('name', sa.Unicode(length=128), nullable=False))
    op.create_foreign_key(None, 'platform', 'account', ['account_id'], ['id'])
    op.drop_constraint(u'user_ibfk_1', 'user', type_='foreignkey')
    op.drop_column('user', 'bot_id')


def downgrade():
    op.add_column('user', sa.Column('bot_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.create_foreign_key(u'user_ibfk_1', 'user', 'bot', ['bot_id'], ['id'])
    op.drop_constraint(None, 'platform', type_='foreignkey')
    op.drop_column('platform', 'name')
    op.drop_column('platform', 'account_id')
    op.add_column('broadcast', sa.Column('message', sa.BLOB(), nullable=False))
    op.drop_constraint(None, 'broadcast', type_='foreignkey')
    op.drop_constraint(None, 'broadcast', type_='foreignkey')
    op.alter_column('broadcast', 'scheduled_time',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.drop_column('broadcast', 'status')
    op.drop_column('broadcast', 'name')
    op.drop_column('broadcast', 'messages')
    op.drop_column('broadcast', 'bot_id')
    op.drop_column('broadcast', 'account_id')
    op.drop_constraint(None, 'bot', type_='foreignkey')
    op.drop_column('bot', 'staging')
    op.drop_column('bot', 'account_id')
    op.drop_constraint(None, 'account', type_='unique')
    op.drop_column('account', 'timezone')
    op.create_table('account_bot',
    sa.Column('account_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('bot_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['account_id'], [u'account.id'], name=u'account_bot_ibfk_1'),
    sa.ForeignKeyConstraint(['bot_id'], [u'bot.id'], name=u'account_bot_ibfk_2'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('bot_def')
