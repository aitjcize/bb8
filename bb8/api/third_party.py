# -*- coding: utf-8 -*-
"""
    Third party web services
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os
import random
import re
import urllib

from cStringIO import StringIO

import cairocffi as cairo
import requests

from backports.functools_lru_cache import lru_cache
from flask import request, make_response, jsonify, render_template

from bb8 import app
from bb8.backend.modules.youbike import GOOGLE_STATIC_MAP_API_KEY


_OMAMORI_BACKGROUND_DIR = '/var/lib/bb8/apps/fortune/resource/backgrounds'

try:
    _OMAMORI_BACKGROUNDS = os.listdir(_OMAMORI_BACKGROUND_DIR)
except Exception:  # This will fail in CI
    _OMAMORI_BACKGROUNDS = []

_OMAMORI_RANDOM_TEXTS = [
    u'九四五三',
    u'九四八七',
    u'九四狂',
    u'BJ4',
    u'LIHO',
    u'不要不要',
    u'了不起，負責',
    u'五十收',
    u'亮亮的蘇美',
    u'你媽超胖',
    u'你沒有妹妹',
    u'先拆坐墊',
    u'公道價八萬一',
    u'北連中胡',
    u'口嫌體正直',
    u'吉好吉滿',
    u'四叉貓',
    u'大guy4醬',
    u'大平台',
    u'大殺四方',
    u'太神了',
    u'好棒棒',
    u'寶寶不說',
    u'小澤愛麗絲',
    u'已知用火',
    u'愛呆丸',
    u'我的滑板鞋',
    u'我難過',
    u'抓泥鰍',
    u'摩擦',
    u'業障重',
    u'母咪',
    u'潮爽德',
    u'火車便當',
    u'神奇寶貝大師',
    u'簽下去',
    u'蒼井空',
    u'藍瘦香菇',
    u'認同請分享',
    u'邊緣人',
    u'酸宗痛',
    u'銅鋰鋅',
    u'雷姆',
    u'馬鷹狗',
    u'魔法師'
]


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
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')

    if not god_name or not ask_god or not imgur_hash or not god_image_url:
        return render_template('error.html')

    fortune_url = 'http://i.imgur.com/%s.png' % imgur_hash
    og_image = request.args.get('og_image', fortune_url)
    og_description = request.args.get('quote', '')
    return render_template('fortune_share.html',
                           og_image=og_image,
                           og_description=og_description,
                           first_name=first_name,
                           last_name=last_name,
                           fortune_url=fortune_url,
                           god_image_url=god_image_url,
                           god_name=god_name,
                           ask_god=ask_god)


def color_code_to_tuple(color_code):
    color_code = color_code.lstrip('#')
    return tuple([ord(x) / 256.0 for x in color_code.decode('hex')])


@app.route('/fortune/omamori')
def fortune_omamori():
    text = request.args.get('text')
    bg_index = request.args.get('bg')

    if not text:
        text = random.choice(_OMAMORI_RANDOM_TEXTS)

    if not bg_index:
        background = random.choice(_OMAMORI_BACKGROUNDS)
    else:
        background = _OMAMORI_BACKGROUNDS[int(bg_index)]

    with open(os.path.join(_OMAMORI_BACKGROUND_DIR, background), 'r') as f:
        surface = cairo.ImageSurface.create_from_png(f)

    cr = cairo.Context(surface)
    font = 'IDDragonXing'
    font_color = color_code_to_tuple(background[:-4])
    font_args = [cairo.FONT_SLANT_NORMAL]

    def draw_char(font_size, offset_x, offset_y, c):
        cr.select_font_face(font, *font_args)
        cr.set_font_size(font_size)
        cr.move_to(offset_x, offset_y)
        cr.text_path(c.encode('utf8'))
        cr.set_source_rgb(*font_color)
        cr.set_line_width(20)
        cr.stroke()

        cr.move_to(offset_x, offset_y)
        cr.text_path(c.encode('utf8'))
        cr.set_source_rgb(1, 1, 1)
        cr.fill()

    if len(text) > 6:
        text = text[:6]

    if len(text) == 1:
        size = 400
        draw_char(size, 320 - size / 2, 700, text[0])
    elif len(text) == 2:
        size = 300
        draw_char(size, 321 - size / 2, 552, text[0])
        draw_char(size, 321 - size / 2, 552 + size + 20, text[1])
    elif len(text) == 3:
        size = 210
        draw_char(size, 321 - size / 2, 482, text[0])
        draw_char(size, 321 - size / 2, 482 + size + 5, text[1])
        draw_char(size, 321 - size / 2, 482 + 2 * size + 10, text[2])
    elif len(text) == 4:
        size = 220
        DX = 10
        DY = 10
        draw_char(size, 321 + DX, 562 - DY, text[0])
        draw_char(size, 321 + DX, 562 + size + DY, text[1])
        draw_char(size, 321 - size - DX, 562 - DY, text[2])
        draw_char(size, 321 - size - DX, 562 + size + DY, text[3])
    elif len(text) == 5:
        size = 200
        DX = 10
        DY = 10
        draw_char(size, 321 + DX, 482 - DY, text[0])
        draw_char(size, 321 + DX, 482 + size + DY, text[1])
        draw_char(size, 321 + DX, 482 + 2 * (size + DY), text[2])
        draw_char(size, 321 - size - DX, 482 - DY + size / 2, text[3])
        draw_char(size, 321 - size - DX, 482 + size + size / 2 + DY, text[4])
    elif len(text) == 6:
        size = 200
        DX = 10
        DY = 10
        draw_char(size, 321 + DX, 482 - DY, text[0])
        draw_char(size, 321 + DX, 482 + size + DY, text[1])
        draw_char(size, 321 + DX, 482 + 2 * (size + DY), text[2])
        draw_char(size, 321 - size - DX, 482 - DY, text[3])
        draw_char(size, 321 - size - DX, 482 + size + DY, text[4])
        draw_char(size, 321 - size - DX, 482 + 2 * (size + DY), text[5])

    buf = StringIO()
    surface.write_to_png(buf)

    response = make_response(buf.getvalue())
    response.headers['content-type'] = 'image/png'

    return response
