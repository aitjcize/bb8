# -*- coding: utf-8 -*-
"""
    Bot Format Parser
    ~~~~~~~~~~~~~~~~~

    Parse a bot from *.bot file

    Copyright 2016 bb8 Authors
"""

import glob
import json
import os
import re
import sys

import jsonschema

from bb8 import config, logger
from bb8.backend.messaging import get_messaging_provider
from bb8.backend.database import (DatabaseManager, Bot, ContentModule, Node,
                                  Platform, PlatformTypeEnum)


def get_bots_dir():
    """Get directory contains bot definitions."""
    backend_dir = os.path.dirname(__file__)
    bots_dir = os.path.normpath(os.path.join(backend_dir, '../../bots'))
    return bots_dir


def get_bot_filename(filename):
    """Get complete filename of bot file."""
    return os.path.join(get_bots_dir(), filename)


def parse_bot(filename, to_bot_id=None):
    """Parse bot from bot definition.

    If *to_bot_id* is specified, update existing bot specified by *to_bot_id*
    instead of creating a new bot.

    If *to_bot_id* is a callable. The result of the call is used as the bot_id.
    """
    schema = None
    bot_json = None
    bot_json_text = None

    with open(get_bot_filename('schema.bot.json'), 'r') as f:
        schema = json.load(f)

    with open(filename, 'r') as f:
        try:
            bot_json_text = f.read()
            bot_json = json.loads(bot_json_text, encoding='utf8')
        except ValueError:
            raise RuntimeError('Invalid JSON file')

    try:
        jsonschema.validate(bot_json, schema)
    except jsonschema.exceptions.ValidationError:
        logger.exception('Validation failed for `%s\'!', filename)
        sys.exit(1)

    bot_desc = bot_json['bot']

    if callable(to_bot_id):
        to_bot_id = to_bot_id(bot_desc)

    if to_bot_id:
        # Update existing bot.
        logger.info('Updating existing bot(id=%d) with %s ...',
                    to_bot_id, filename)
        for platform_desc in bot_json['platforms']:
            ptype = PlatformTypeEnum(platform_desc['type_enum'])
            provider = get_messaging_provider(ptype)
            try:
                jsonschema.validate(platform_desc['config'],
                                    provider.get_config_schema())
            except jsonschema.exceptions.ValidationError:
                logger.error('Platform `%s\' config validation failed',
                             platform_desc['type_enum'])
                raise

            if (not platform_desc['deployed'] or
                    (config.DEPLOY and platform_desc['deployed'])):
                provider.apply_config(platform_desc['config'])

        bot = Bot.get_by(id=to_bot_id, single=True)
        bot.delete_all_node_and_links()  # Delete all previous node and links

        bot.name = bot_desc['name']
        bot.description = bot_desc['description']
        bot.interaction_timeout = bot_desc['interaction_timeout']
        bot.admin_interaction_timeout = bot_desc['admin_interaction_timeout']
        bot.session_timeout = bot_desc['session_timeout']
        bot.ga_id = bot_desc.get('ga_id', None)
        DatabaseManager.flush()
    else:  # Create a new bot
        logger.info('Creating new bot from %s ...', filename)
        bot = Bot(
            name=bot_desc['name'],
            description=bot_desc['description'],
            interaction_timeout=bot_desc['interaction_timeout'],
            admin_interaction_timeout=bot_desc['admin_interaction_timeout'],
            session_timeout=bot_desc['session_timeout'],
            ga_id=bot_desc.get('ga_id', None)).add()
        DatabaseManager.flush()

        for platform_desc in bot_json['platforms']:
            ptype = PlatformTypeEnum(platform_desc['type_enum'])
            provider = get_messaging_provider(ptype)
            try:
                jsonschema.validate(platform_desc['config'],
                                    provider.get_config_schema())
            except jsonschema.exceptions.ValidationError:
                logger.error('Platform `%s\' config validation failed',
                             platform_desc['type_enum'])
                raise

            Platform(bot_id=bot.id,
                     type_enum=platform_desc['type_enum'],
                     provider_ident=platform_desc['provider_ident'],
                     config=platform_desc['config']).add()

            if (not platform_desc['deployed'] or
                    (config.DEPLOY and platform_desc['deployed'])):
                provider.apply_config(platform_desc['config'])

    nodes = bot_desc['nodes']
    name_id_map = {}

    # Build node
    for name, node in nodes.iteritems():
        try:
            cm = ContentModule.get_by(id=node['content_module']['id'],
                                      single=True)
            jsonschema.validate(node['content_module']['config'],
                                cm.get_module().schema())
        except jsonschema.exceptions.ValidationError:
            logger.error('Node `%s\' content module config validation '
                         'failed', node['name'])
            raise

        n = Node(bot_id=bot.id, name=unicode(node['name']),
                 description=unicode(node['description']),
                 expect_input=node['expect_input'],
                 content_module_id=node['content_module']['id'],
                 content_config=node['content_module']['config']).add()

        if 'parser_module' in node:
            n.parser_module_id = node['parser_module']['id']

        DatabaseManager.flush()
        name_id_map[name] = n.id

    # Set bot start, root node
    bot.start_node_id = name_id_map['start']
    bot.root_node_id = name_id_map['root']

    # Build linkage
    node_re = re.compile(r'"\[\[(.*?)\]\]"')

    def replace_node_id(m):
        name = m.group(1)
        if name in name_id_map:
            return str(name_id_map[name])
        return m.group(0)

    bot_json_text = node_re.sub(replace_node_id, bot_json_text)
    bot_json = json.loads(bot_json_text, encoding='utf8')

    for name, node in nodes.iteritems():
        n = Node.get_by(id=name_id_map[name], single=True)
        if n.parser_module is not None:
            nodes = bot_json['bot']['nodes']
            n.parser_config = nodes[name]['parser_module']['config']
            pm = n.parser_module.get_module()
            try:
                jsonschema.validate(n.parser_config, pm.schema())
            except jsonschema.exceptions.ValidationError:
                logger.error('Node `%s\' parser module config validation '
                             'failed', node['name'])
                raise

            n.build_linkages(pm.get_linkages(n.parser_config))

    DatabaseManager.flush()
    return bot


def build_all_bots():
    """Re-build all bots from bot definitions."""
    for bot in glob.glob(get_bots_dir() + '/*.bot'):
        parse_bot(bot)


def update_all_bots():
    """Update all bots from bot definitions."""
    def find_bot_by_name(bot_desc):
        bot = Bot.get_by(name=bot_desc['name'], single=True)
        if bot:
            return bot.id
        else:
            return None

    for bot in glob.glob(get_bots_dir() + '/*.bot'):
        parse_bot(bot, find_bot_by_name)
