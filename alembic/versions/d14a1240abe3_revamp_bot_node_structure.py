"""revamp bot node structure

Revision ID: d14a1240abe3
Revises: a4a08467bfb4
Create Date: 2016-11-17 17:16:53.875003

"""

# revision identifiers, used by Alembic.
revision = 'd14a1240abe3'
down_revision = 'a4a08467bfb4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('module',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('type', sa.Enum('Content', 'Parser', 'Router', name='moduletypeenum'), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('supported_platform', sa.Enum('All', 'Facebook', 'Line', name='supportedplatform'), nullable=False),
    sa.Column('module_name', sa.String(length=256), nullable=False),
    sa.Column('variables', sa.PickleType(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('parser_module')
    op.drop_table('content_module')
    op.add_column('node', sa.Column('config', sa.PickleType(), nullable=False))
    op.add_column('node', sa.Column('module_id', sa.String(length=128), nullable=False))
    op.add_column('node', sa.Column('next_node_id', sa.String(length=128), nullable=True))
    op.alter_column('node', 'description',
               existing_type=mysql.TEXT(collation=u'utf8_unicode_ci'),
               nullable=False)
    op.drop_constraint(u'node_ibfk_2', 'node', type_='foreignkey')
    op.drop_constraint(u'node_ibfk_3', 'node', type_='foreignkey')
    op.create_foreign_key(None, 'node', 'module', ['module_id'], ['id'])
    op.drop_column('node', 'parser_module_id')
    op.drop_column('node', 'parser_config')
    op.drop_column('node', 'content_config')
    op.drop_column('node', 'content_module_id')


def downgrade():
    op.add_column('node', sa.Column('content_module_id', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=128), nullable=False))
    op.add_column('node', sa.Column('content_config', sa.BLOB(), nullable=False))
    op.add_column('node', sa.Column('parser_config', sa.BLOB(), nullable=True))
    op.add_column('node', sa.Column('parser_module_id', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=128), nullable=True))
    op.drop_constraint(None, 'node', type_='foreignkey')
    op.create_foreign_key(u'node_ibfk_3', 'node', 'parser_module', ['parser_module_id'], ['id'])
    op.create_foreign_key(u'node_ibfk_2', 'node', 'content_module', ['content_module_id'], ['id'])
    op.alter_column('node', 'description',
               existing_type=mysql.TEXT(collation=u'utf8_unicode_ci'),
               nullable=True)
    op.drop_column('node', 'next_node_id')
    op.drop_column('node', 'module_id')
    op.drop_column('node', 'config')
    op.create_table('content_module',
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.Column('id', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=128), nullable=False),
    sa.Column('name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('description', mysql.TEXT(collation=u'utf8_unicode_ci'), nullable=False),
    sa.Column('supported_platform', mysql.ENUM(u'All', u'Facebook', u'Line', collation=u'utf8_unicode_ci'), nullable=False),
    sa.Column('module_name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('ui_module_name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('parser_module',
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.Column('id', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=128), nullable=False),
    sa.Column('name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('description', mysql.TEXT(collation=u'utf8_unicode_ci'), nullable=False),
    sa.Column('supported_platform', mysql.ENUM(u'All', u'Facebook', u'Line', collation=u'utf8_unicode_ci'), nullable=False),
    sa.Column('module_name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('ui_module_name', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=256), nullable=False),
    sa.Column('variables', sa.BLOB(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('module')
