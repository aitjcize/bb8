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

from bb8.backend.database import Bot, DatabaseSession, Node, Platform


def parse_bot(filename):
    """Parse bot from bot definition."""
    # TODO(aitjcize): add *.bot schema and schema validation

    bot_json = None
    bot_json_text = None

    with open(filename, 'r') as f:
        try:
            bot_json_text = f.read()
            bot_json = json.loads(bot_json_text, encoding='utf8')
        except ValueError:
            raise RuntimeError('Invalid JSON file')

    platform_desc = bot_json['platform']
    bot_desc = bot_json['bot']

    bot = Bot(name=bot_desc['name'], description=bot_desc['description'],
              interaction_timeout=bot_desc['interaction_timeout'],
              session_timeout=bot_desc['session_timeout']).add()
    bot.commit()

    platform = Platform(bot_id=bot.id, **platform_desc).add()
    platform.commit()

    nodes = bot_desc['nodes']
    name_id_map = {}

    # Build node
    for name, node in nodes.iteritems():
        n = Node(bot_id=bot.id, name=node['name'],
                 description=node['description'],
                 expect_input=node['expect_input'],
                 content_module_id=node['content_module']['id'],
                 content_config=node['content_module']['config']).add()

        if 'parser_module' in node:
            n.parser_module_id = node['parser_module']['id']

        n.commit()
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
            n.build_linkages(pm.get_linkages(n.parser_config))


def build_all_bots():
    """Re-build all bots from bot definitions."""
    backend_dir = os.path.dirname(__file__)
    bots_dir = os.path.normpath(os.path.join(backend_dir, '../../bots'))

    bots = glob.glob(bots_dir + '/*.bot')

    with DatabaseSession():
        for bot in bots:
            parse_bot(bot)
