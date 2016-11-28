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

import jsonschema

import bb8
from bb8 import config, logger
from bb8 import util
from bb8.backend.messaging import get_messaging_provider
from bb8.backend.database import (DatabaseManager, Bot, Module, Node, Platform,
                                  ModuleTypeEnum)


HAS_VARIABLE_RE = re.compile('{{(.*?)}}')


def get_bots_dir():
    """Get directory contains bot definitions."""
    return os.path.join(bb8.SRC_ROOT, 'bots')


def get_bot_filename(filename):
    """Get complete filename of bot file."""
    return os.path.join(get_bots_dir(), filename)


def validate_bot_schema(bot_json, source='bot_json'):
    try:
        schema = util.get_schema('bot')
        jsonschema.validate(bot_json, schema)
    except jsonschema.exceptions.ValidationError:
        logger.error('Validation failed for `%s\'!', source)
        raise


def parse_bot(bot_json, to_bot_id=None, source='bot_json'):
    """Parse Bot from bot definition.

    If *to_bot_id* is specified, update existing bot specified by *to_bot_id*
    instead of creating a new bot.

    If *to_bot_id* is a callable. The result of the call is used as the bot_id.
    """
    validate_bot_schema(bot_json, source=source)

    bot_desc = bot_json['bot']

    if callable(to_bot_id):
        to_bot_id = to_bot_id(bot_desc)

    if to_bot_id:
        # Update existing bot.
        logger.info(u'Updating existing Bot(id=%d, name=%s) from %s ...',
                    to_bot_id, bot_desc['name'], source)

        bot = Bot.get_by(id=to_bot_id, single=True)
        bot.delete_all_nodes()
        bot.name = bot_desc['name']
        bot.description = bot_desc['description']
        bot.interaction_timeout = bot_desc['interaction_timeout']
        bot.admin_interaction_timeout = bot_desc['admin_interaction_timeout']
        bot.session_timeout = bot_desc['session_timeout']
        bot.ga_id = bot_desc.get('ga_id', None)
        bot.settings = bot_desc['settings']
        DatabaseManager.flush()
    else:
        # Create a new bot
        logger.info(u'Creating new Bot(name=%s) from %s ...',
                    bot_desc['name'], source)
        bot = Bot(
            name=bot_desc['name'],
            description=bot_desc['description'],
            interaction_timeout=bot_desc['interaction_timeout'],
            admin_interaction_timeout=bot_desc['admin_interaction_timeout'],
            session_timeout=bot_desc['session_timeout'],
            ga_id=bot_desc.get('ga_id', None),
            settings=bot_desc['settings']).add()
        DatabaseManager.flush()

    # Bind Platform with Bot
    platforms = bot_json.get('platforms', {})
    for unused_name, provider_ident in platforms.iteritems():
        platform = Platform.get_by(provider_ident=provider_ident, single=True)
        if platform is None:
            raise RuntimeError('associated platform `%s\' does not exist',
                               provider_ident)

        # Bind
        platform.bot_id = bot.id

        provider = get_messaging_provider(platform.type_enum)
        if not platform.deployed or (config.DEPLOY and platform.deployed):
            provider.apply_settings(platform.config, bot.settings)

        DatabaseManager.flush()

    nodes = bot_desc['nodes']
    id_map = {}  # Mapping of stable_id to id

    # Build node
    for stable_id, node in nodes.iteritems():
        try:
            m = Module.get_by(id=node['module']['id'], single=True)
            if m is None:
                raise RuntimeError('Module `%s\' does not exist' %
                                   node['module']['id'])
            jsonschema.validate(node['module']['config'],
                                m.get_python_module().schema())
        except jsonschema.exceptions.ValidationError:
            logger.error('Node `%s\' module config validation '
                         'failed', stable_id)
            raise

        n = Node(stable_id=stable_id, bot_id=bot.id,
                 name=unicode(node['name']),
                 description=unicode(node.get('description', '')),
                 expect_input=node['expect_input'],
                 next_node_id=node.get('next_node_id'),
                 module_id=node['module']['id'],
                 config=node['module']['config']).add()

        DatabaseManager.flush()
        id_map[stable_id] = n.id

    # Validate that module linkages are present in this bot file.
    for stable_id, node in nodes.iteritems():
        n = Node.get_by(id=id_map[stable_id], single=True)
        if n.module.type != ModuleTypeEnum.Router:
            if n.next_node_id:
                if re.search(HAS_VARIABLE_RE, n.next_node_id):
                    logger.info('Rendered next_node_id `%s\', check '
                                'skipped ...' % n.next_node_id)
                    continue
                elif n.next_node_id not in id_map.keys():
                    raise RuntimeError(
                        'next_node_id `%s\' is invalid for node `%s\'' %
                        (n.next_node_id, n.stable_id))
        else:
            pm = n.module.get_python_module()
            for end_node_id in pm.get_linkages(n.config):
                if end_node_id is not None:
                    if re.search(HAS_VARIABLE_RE, end_node_id):
                        logger.info('Rendered end_node_id `%s\', check '
                                    'skipped ...' % end_node_id)
                        continue
                    if end_node_id not in id_map.keys():
                        raise RuntimeError('end_node_id `%s\' is invalid' %
                                           end_node_id)
    # Extra Constraint check
    root = Node.get_by(stable_id='Root', single=True)
    root_router = Node.get_by(stable_id='RootRouter', single=True)

    if root.next_node_id != 'RootRouter':
        raise RuntimeError('next_node_id for Root must be RootRouter')

    if root_router.next_node_id != 'Root':
        raise RuntimeError('next_node_id for RootRouter must be Root')

    DatabaseManager.flush()
    return bot


def parse_bot_from_file(filename, to_bot_id=None):
    """Parse Bot from bot definition from file."""
    with open(filename, 'r') as f:
        try:
            bot_json = json.load(f, encoding='utf8')
        except ValueError as e:
            raise RuntimeError('Invalid JSON file: %s' % e)

    return parse_bot(bot_json, to_bot_id, filename)


def build_all_bots():
    """Build all bots from bot definitions."""
    for bot in glob.glob(get_bots_dir() + '/*.bot'):
        parse_bot_from_file(bot)


def update_all_bots():
    """Update all bots from bot definitions."""
    def find_bot_by_name(bot_desc):
        bot = Bot.get_by(name=bot_desc['name'], single=True)
        if bot:
            return bot.id
        else:
            return None

    for bot in glob.glob(get_bots_dir() + '/*.bot'):
        parse_bot_from_file(bot, find_bot_by_name)
