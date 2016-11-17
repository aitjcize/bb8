# -*- coding: utf-8 -*-
"""
    List website elements as cards
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import urllib
import urllib2

from bb8.backend.module_api import (Message, Resolve, ModuleTypeEnum,
                                    SupportedPlatform, TextPayload,
                                    PureContentModule)


DEFAULT_TIMEOUT_SECS = 5


def properties():
    return {
        'id': 'ai.compose.content.core.listing',
        'type': ModuleTypeEnum.Content,
        'name': 'Listing',
        'description': 'List website elements as cards',
        'supported_platform': SupportedPlatform.All,
        'variables': []
    }


def schema():
    return {
        'type': 'object',
        'required': ['query_url', 'max_count', 'list', 'attributes'],
        'properties': {
            'query_url': {'type': 'string'},
            'timeout_secs': {'type': 'integer'},
            'max_count': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 7
            },
            'list': {'type': 'string'},
            'attributes': {
                'type': 'object',
                'required': ['image', 'title'],
                'properties': {
                    'title': {'type': 'string'},
                    'image': {'type': 'string'},
                    'item_url': {'type': 'string'},
                    'subtitle': {'type': 'string'},
                    'buttons': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/button'}
                    }
                }
            }
        },
        'definitions': {
            'button': Message.Button.schema()
        }
    }


@PureContentModule
def run(content_config, unused_env, variables):
    """
    content_config schema:
    {
        "query_url": "http://ecshweb.pchome.com.tw/search/v3.3/all/results?"
                     "q=%s&page=1&sort=rnk/dc",
        "term": "{{matches#1}}",
        "max_count": 7,
        "list": "prods",
        "attributes": {
              "title": "${{price}}: {{name}}",
              "image": "http://a.ecimg.tw/{{picB}}",
              "item_url": "http://24h.pchome.com.tw/{{Id}}",
              "subtitle": "{{describe}}",
              "buttons": [
                  {
                      "type": "web_url",
                      "title": "商品頁面",
                      "url": "http://24h.pchome.com.tw/{{Id}}"
                  }
              ]
          }
    }
    """
    url = content_config['query_url']
    timeout = content_config.get('timeout_secs', DEFAULT_TIMEOUT_SECS)

    if 'term' in content_config:
        term = Resolve(content_config['term'], variables)
        url = url % urllib.quote(term.encode('utf-8'))

    try:
        content = json.loads(urllib2.urlopen(url, timeout=timeout).read())
    except Exception:
        return []

    max_count = content_config['max_count']
    attributes = content_config['attributes']
    elements = content.get(content_config['list'], [])

    if len(elements) > max_count:
        elements = elements[:max_count]

    m = Message()
    for element in elements:
        var = dict(variables, **element)
        bub = Message.Bubble(
            title=attributes['title'],
            item_url=attributes.get('item_url', None),
            image_url=attributes['image'],
            subtitle=attributes.get('subtitle', None),
            variables=var)

        for b in attributes.get('buttons', []):
            payload = b.get('payload', None)
            bub.add_button(Message.Button(
                b_type=Message.ButtonType(b['type']),
                title=b['title'],
                url=b.get('url', None),
                payload=TextPayload(payload) if payload else None,
                variables=var))

        m.add_bubble(bub)

    return [m]
