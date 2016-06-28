#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Modify bot for testing
    ~~~~~~~~~~~~~~~~~~~~~~

    Replace the Platform array in bot config and generate new testing bot.

    Copyright 2016 bb8 Authors
"""

from __future__ import print_function

import argparse
import json
import os
import re
import sys


def mod_bot_for_testing(bot, platform):
    """Modify existing bot to use a pre-set test platform config.

    For example:

    Given youbike.bot and bb8.facebook.platform, output a new bot
    youbike.bb8.facebook.bot.
    """
    real_file_path = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.normpath(os.path.join(real_file_path, '..', '..'))

    bots_dir = os.path.join(project_root, 'bots')
    platforms_dir = os.path.join(project_root, 'dev', 'platforms')

    bot_file = os.path.join(bots_dir, '%s.bot' % bot)
    platform_file = os.path.join(platforms_dir, '%s.platform' % platform)

    if not os.path.exists(bot_file):
        raise RuntimeError('Bot `%s\' does not exist' % bot_file)

    if not os.path.exists(platform_file):
        raise RuntimeError('Platform `%s\' does not exist' % platform_file)

    print('Reading bot and platform definitions ...')
    with open(bot_file) as f:
        bot_json = json.load(f)

    with open(platform_file) as f:
        platform_json = json.load(f)

    print('Modifying bot ...')
    bot_json['platforms'] = platform_json['platforms']

    def to_unicode(m):
        return unicode(m.group(0)).decode('unicode-escape')

    outfile = os.path.join(bots_dir, '%s.%s.bot' % (bot, platform))
    with open(outfile, 'w') as f:
        data = unicode(json.dumps(bot_json, indent=2))
        data = re.sub(', $', ',', data, flags=re.M)
        data = re.sub(r'\\u[0-9a-f]{4}', to_unicode, data, flags=re.M)
        f.write(data.encode('utf8'))

    print('Test bot created as `%s.%s.bot\'.' % (bot, platform))


def main():
    parser = argparse.ArgumentParser(description='Modify bot for testing')
    parser.add_argument('bot', help='name of bot to modify')
    parser.add_argument('platform', help='name of platofrm config file')

    args = parser.parse_args()
    try:
        mod_bot_for_testing(args.bot, args.platform)
    except Exception as e:
        print('Error: %s' % e)
        sys.exit(1)


if __name__ == '__main__':
    main()
