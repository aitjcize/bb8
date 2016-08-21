"""remove uneeded content tables

Revision ID: 420ba26be66b
Revises: c9d6ce4066e5
Create Date: 2016-08-18 18:44:28.244218

"""

# revision identifiers, used by Alembic.
revision = '420ba26be66b'
down_revision = 'c9d6ce4066e5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_table('entry')
    op.drop_table('entry_tag')
    op.drop_table('tag')


def downgrade():
    op.create_table('tag',
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('entry_tag',
    sa.Column('entry_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('tag_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['entry_id'], [u'entry.id'], name=u'entry_tag_ibfk_1'),
    sa.ForeignKeyConstraint(['tag_id'], [u'tag.id'], name=u'entry_tag_ibfk_2'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('entry',
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('account_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('title', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=128), nullable=False),
    sa.Column('link', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('description', mysql.TEXT(collation=u'utf8_unicode_ci'), nullable=False),
    sa.Column('publish_time', mysql.DATETIME(), nullable=False),
    sa.Column('source_name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=64), nullable=False),
    sa.Column('image_url', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('author', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=64), nullable=False),
    sa.Column('content', mysql.TEXT(collation=u'utf8_unicode_ci'), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], [u'account.id'], name=u'entry_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
