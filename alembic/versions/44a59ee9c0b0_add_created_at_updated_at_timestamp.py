"""add created_at, updated_at timestamp

Revision ID: 44a59ee9c0b0
Revises: All tables
Create Date: 2016-06-21 15:01:43.158273

"""

# revision identifiers, used by Alembic.
revision = '44a59ee9c0b0'
down_revision = None
branch_labels = None
depends_on = None

import datetime
import inspect

from alembic import op
import sqlalchemy as sa

from bb8.backend import database


def upgrade():
    op.add_column('account', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('account', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('bot', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('bot', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('broadcast', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('broadcast', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('colleted_data', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('colleted_data', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('content_module', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('content_module', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('conversation', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('conversation', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('entry', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('entry', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('event', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('event', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('feed', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('feed', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('linkage', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('linkage', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('node', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('node', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('oauth_info', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('oauth_info', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('parser_module', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('parser_module', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('platform', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('platform', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('public_feed', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('public_feed', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('tag', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('tag', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=False))

    # Populate with default values
    for obj_name in dir(database):
        obj = getattr(database, obj_name)
        if (inspect.isclass(obj) and issubclass(obj, database.ModelMixin)
            and obj != database.ModelMixin):
            now = datetime.datetime.utcnow()
            op.execute(
                obj.__table__.update().values({
                    obj.created_at: now,
                    obj.updated_at: now
                })
            )


def downgrade():
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('tag', 'updated_at')
    op.drop_column('tag', 'created_at')
    op.drop_column('public_feed', 'updated_at')
    op.drop_column('public_feed', 'created_at')
    op.drop_column('platform', 'updated_at')
    op.drop_column('platform', 'created_at')
    op.drop_column('parser_module', 'updated_at')
    op.drop_column('parser_module', 'created_at')
    op.drop_column('oauth_info', 'updated_at')
    op.drop_column('oauth_info', 'created_at')
    op.drop_column('node', 'updated_at')
    op.drop_column('node', 'created_at')
    op.drop_column('linkage', 'updated_at')
    op.drop_column('linkage', 'created_at')
    op.drop_column('feed', 'updated_at')
    op.drop_column('feed', 'created_at')
    op.drop_column('event', 'updated_at')
    op.drop_column('event', 'created_at')
    op.drop_column('entry', 'updated_at')
    op.drop_column('entry', 'created_at')
    op.drop_column('conversation', 'updated_at')
    op.drop_column('conversation', 'created_at')
    op.drop_column('content_module', 'updated_at')
    op.drop_column('content_module', 'created_at')
    op.drop_column('colleted_data', 'updated_at')
    op.drop_column('colleted_data', 'created_at')
    op.drop_column('broadcast', 'updated_at')
    op.drop_column('broadcast', 'created_at')
    op.drop_column('bot', 'updated_at')
    op.drop_column('bot', 'created_at')
    op.drop_column('account', 'updated_at')
    op.drop_column('account', 'created_at')
