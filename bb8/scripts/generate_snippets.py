#!/usr/bin/env python
"""
    Scripts for generate SnipMate snippets
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Run `./generate_snippets.py` and it will generate a `json.snippets`

    Please `bots/README.md` for instructions on how to use snippets.

    Copyright 2017 bb8 Authors
"""

from __future__ import print_function

import importlib
import os

from bb8.backend.modules import list_all_modules
from bb8.util import get_schema
from bb8.backend.database import Module


def _generate_snippet(snippets, key, obj):
    output = []
    index = 1

    if 'patternProperties' in obj and 'required' in obj:
        obj['properties'] = {prop: {'type': 'object'}
                             for prop in obj['required']}

    if 'properties' not in obj:
        return

    for prop, value in obj['properties'].iteritems():
        if 'type' not in value and '$ref' in value:
            value['type'] = os.path.basename(value['$ref'])

        if 'type' not in value:
            value['type'] = 'null'

        if isinstance(value['type'], list):
            value['type'] = ','.join(x for x in value['type'])

        if 'default' in value:
            default = value['default']
        else:
            default = (('' if prop in obj.get('required', []) else 'opt;') +
                       value['type'])

        placeholder = '${%d:%s}' % (index, default)
        index += 1

        if value['type'] == 'string':
            placeholder = '"%s"' % placeholder

        output.append('  "%s": %s' % (prop, placeholder))

        if value['type'] == 'object':
            _generate_snippet(snippets, prop, value)
        elif value['type'] == 'array':
            _generate_snippet(snippets, '%s.items' % prop, value['items'])

    json_output = '{\n%s\n}' % ',\n'.join(output)

    if 'definitions' in obj:
        for k, v in obj['definitions'].iteritems():
            _generate_snippet(snippets, k, v)

    snippets[key] = json_output


def generate_snippet(key, obj):
    snippets = {}
    _generate_snippet(snippets, key, obj)
    return snippets


def generate_snipmate_snippets(snippets, filename):
    with open(filename, 'w') as f:
        for k, v in snippets.iteritems():
            f.write('snippet %s\n' % k)
            f.write('\n'.join(['\t' + line for line in v.split('\n')]))
            f.write('\n')


def main():
    # Generate snipets for bot and all module configs
    snippets = generate_snippet('botfile', get_schema('bot'))

    for name in list_all_modules():
        print('Reading schema for module `%s\' ...' % name)
        m = importlib.import_module('%s.%s' %
                                    (Module.MODULE_PACKAGE, name))
        if not hasattr(m, 'schema'):
            print('Skip module %s due to lack of schema()' % name)
            continue

        s = generate_snippet(name, m.schema())
        snippets = dict(snippets, **s)

    generate_snipmate_snippets(snippets, 'json.snippets')


if __name__ == '__main__':
    main()
