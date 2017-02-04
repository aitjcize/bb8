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
from flask import request, make_response, jsonify, render_template

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


@app.route('/fortune_share/<imgur_hash>', methods=['GET'])
def fortune_share_facebook(imgur_hash):
    """Share the result of fortune bot"""
    god_name = request.args.get('god_name', None)
    ask_god = request.args.get('ask_god', None)
    god_image_url = request.args.get('god_image_url', None)

    if not god_name or not ask_god or not imgur_hash or not god_image_url:
        return render_template('error.html')

    fortune_url = 'http://i.imgur.com/%s.png' % imgur_hash
    og_image = request.args.get('og_image', fortune_url)
    og_description = request.args.get('quote', '')
    return render_template('fortune_share.html',
                           og_image=og_image,
                           og_description=og_description,
                           fortune_url=fortune_url,
                           god_image_url=god_image_url,
                           god_name=god_name,
                           ask_god=ask_god)
