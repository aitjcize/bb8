"""add thread, label implementation

Revision ID: bf21e1cf4597
Revises: d14a1240abe3
Create Date: 2016-11-27 10:09:25.168681

"""

# revision identifiers, used by Alembic.
revision = 'bf21e1cf4597'
down_revision = 'd14a1240abe3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('account_user',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=256), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('email_verified', sa.Boolean(), nullable=False),
    sa.Column('passwd', sa.String(length=256), nullable=False),
    sa.Column('timezone', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('label',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.Unicode(length=32), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('account_id', 'name')
    )
    op.create_table('user_label',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('label_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['label_id'], ['label.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.drop_index('email', table_name='account')
    op.create_unique_constraint(None, 'account', ['name'])
    op.drop_column(u'account', 'passwd')
    op.drop_column(u'account', 'email_verified')
    op.drop_column(u'account', 'email')
    op.drop_column(u'account', 'timezone')
    op.add_column(u'conversation', sa.Column('sender', sa.Integer(), nullable=True))
    op.add_column(u'conversation', sa.Column('timestamp', sa.Float(), nullable=False))
    op.create_foreign_key(None, 'conversation', 'account_user', ['sender'], ['id'])
    op.add_column(u'oauth_info', sa.Column('account_user_id', sa.Integer(), nullable=False))
    op.drop_constraint(u'oauth_info_ibfk_1', 'oauth_info', type_='foreignkey')
    op.create_foreign_key(None, 'oauth_info', 'account_user', ['account_user_id'], ['id'])
    op.drop_column(u'oauth_info', 'account_id')
    op.add_column(u'user', sa.Column('assignee', sa.Integer(), nullable=True))
    op.add_column(u'user', sa.Column('comment', sa.UnicodeText(), nullable=True))
    op.add_column(u'user', sa.Column('status', sa.Enum('Archived', 'Assigned', 'Closed', 'Open', 'Read', 'Unread', name='threadstatusenum'), nullable=True))
    op.create_foreign_key(None, 'user', 'account_user', ['assignee'], ['id'])
    op.drop_column(u'user', 'login_token')


def downgrade():
    op.add_column(u'user', sa.Column('login_token', mysql.TEXT(collation=u'utf8_unicode_ci'), nullable=True))
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column(u'user', 'status')
    op.drop_column(u'user', 'comment')
    op.drop_column(u'user', 'assignee')
    op.add_column(u'oauth_info', sa.Column('account_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'oauth_info', type_='foreignkey')
    op.create_foreign_key(u'oauth_info_ibfk_1', 'oauth_info', 'account', ['account_id'], ['id'])
    op.drop_column(u'oauth_info', 'account_user_id')
    op.drop_constraint(None, 'conversation', type_='foreignkey')
    op.drop_column(u'conversation', 'timestamp')
    op.drop_column(u'conversation', 'sender')
    op.add_column(u'account', sa.Column('timezone', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=32), nullable=False))
    op.add_column(u'account', sa.Column('email', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False))
    op.add_column(u'account', sa.Column('email_verified', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.add_column(u'account', sa.Column('passwd', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False))
    op.drop_constraint(None, 'account', type_='unique')
    op.create_index('email', 'account', ['email'], unique=True)
    op.drop_table('user_label')
    op.drop_table('label')
    op.drop_table('account_user')
