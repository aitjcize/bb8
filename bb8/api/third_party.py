# -*- coding: utf-8 -*-
"""
    Third party web services
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import re
import urllib

import requests

from backports.functools_lru_cache import lru_cache
from flask import request, make_response, jsonify

from bb8 import app
from bb8.backend.modules.youbike import GOOGLE_STATIC_MAP_API_KEY


@app.route('/api/third_party/youbike/render_map')
def redirect_render_map():
    """Workaround facebooks 'bug', wher it remove multiple value with same key.
    We use facebook to pass the arguments, then request render from Google on
    behalf of it."""

    url = request.args.get('url', None)
    if not url:
        return 'No URL specified'

    url = urllib.unquote(url + '&key=' + GOOGLE_STATIC_MAP_API_KEY)
    h = urllib.urlopen(url)
    response = make_response(h.read())
    response.headers['content-type'] = h.headers['content-type']

    return response


@lru_cache(maxsize=1024)
def duckduckgo_image_search(q):
    res = requests.get('https://duckduckgo.com/?q=%s&iax=1&ia=images' % q)
    res.raise_for_status()

    m = re.search('vqd=\'(.*?)\'', res.text)
    if not m:
        return 'Not found', 404

    vqd = m.group(1)

    res = requests.get(
        'https://duckduckgo.com/i.js?l=zh-tw&o=json&q=%s&vqd=%s' % (q, vqd))
    res.raise_for_status()

    return res.json()


@app.route('/api/third_party/fortune/image_search')
def fortune_image_search():
    q = request.args['q']
    return jsonify(duckduckgo_image_search(q))
