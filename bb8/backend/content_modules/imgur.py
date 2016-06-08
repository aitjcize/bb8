# -*- coding: utf-8 -*-
"""
    Send imgur images as cards
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import random

import imgurpython

from imgurpython.imgur.models.gallery_image import GalleryImage

from bb8.backend.module_api import Message, Payload, Resolve


def get_module_info():
    return {
        'id': 'ai.compose.third_party.imgur',
        'name': 'Imgur',
        'description': 'Imgur image search and listing.',
        'module_name': 'imgur',
        'ui_module_name': 'imgur',
    }


def run(content_config, env, variables):
    """
    content_config schema:
    {
       "type": "random or query",
       "term": "query term if type is query",
       "max_count": 5, // max number of images to return
       "auth": {
           "client_id": "imgur client_id",
           "client_secret": "imgur client_secret"
       }
    }
    """
    client = imgurpython.ImgurClient(content_config['auth']['client_id'],
                                     content_config['auth']['client_secret'])

    if content_config['type'] == 'random':
        images = [x for x in client.gallery_random() if
                  isinstance(x, GalleryImage)]
    else:
        term = Resolve(content_config['term'], variables)
        images = [x for x in client.gallery_search(term) if
                  isinstance(x, GalleryImage)]

    images = random.sample(images, int(content_config['max_count']))

    m = Message()
    for i in images:
        c = Message.Bubble(i.title, i.link[:-4], i.link,
                           i.description)
        c.add_button(Message.Button(Message.ButtonType.WEB_URL, 'Source',
                                    url=i.link[:-4]))
        c.add_button(Message.Button(Message.ButtonType.POSTBACK, 'Like',
                                    payload=Payload('like %s' % i.link, env)))
        m.add_bubble(c)

    return [Message('Here are the images you requested'), m]
