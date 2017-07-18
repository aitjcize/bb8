#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is to handle the AJAX request and output commando format.

TODO: This file will be migrated to bb8 backend module.

Note that all JSON inputs are unicode-encoded.
"""

import datetime
import json
import logging
import random
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import ajax_helper
import utils
import fund
import people
import want

"""
    Example: http://192.168.87.2:7788/want_ajax?action=NextFoodsToChoose&
                input=["\u96de\u817f\u98ef", "-\u8089\u71e5\u98ef"]

    Use the following script to generate:
      >>> import json
      >>> json.dumps([u'飯',u'-麵',u'+湯'])
"""
class WantAjax(ajax_helper.AjaxHelper):

  def __init__(self, request, response):
    self.initialize(request, response)
    ajax_helper.AjaxHelper.methods = self
    self.accept_langs = utils.getAcceptLanguage(self)

  def GetRecommendedFoods(self):
    """Get recommendation according to user's inputs.

    Args:
      Common:
        user_lang=zh_TW
        selected=["+羊肉爐", "+漢堡", "+洋蔥", "+肉圓", "+豆腐鍋"]
      Web:
        local_langs=[["zh_TW", 1.0]]
      Comopse.ai:
        location={u'coordinates': {u'lat': 25.0339031, u'long': 121.5645099}}
        platform_user_ident=1115862448503460

    Returns:
      list of a dict:
    """
    selected = json.loads(self.request.get("selected"))
    user_lang = self.request.get("user_lang")

    logging.debug('selected: %r', selected)
    logging.debug('user_lang: %r', user_lang)

    foods = want.get_recommended_foods(selected, user_lang, [[user_lang, 1.0]])

    # remove score before sending to client.
    for r in foods:
      del r["score"]

    # Return partial list to save bandwidth and not to leak the table.
    msgs = []
    elements = []
    for food in foods[:3]:

      f = fund.data[food['food']]
      elements.append({
          'image_url': f['image_url'],
          'item_url': f['item_url'],
          'title': f['display_name'],
          'subtitle': f['desc'],
          'buttons': [{
            'type': 'web_url',
            'title': '基金介紹',
            'url': f['item_url'],
          }],
      })

    msgs.append({
        'text': '以下是我們認為你可能會喜歡的基金： 💋 ',
    })
    msgs.append({
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': 'generic',
                'elements': elements,
            },
        }
    })

    """FIXME: remove me
    why = '為什麼我們推薦你這些基金？因為你喜歡這些人：'
    like_count = 0
    for person in selected:
      if person.startswith('+'):
        like_count += 1
        name = person[1:].encode('utf-8')
        intro = people.data[name]['desc']
        why += name + '：' + intro + '。'

    # Line has limitation for max 5 messages. Compress the reasons.
    if like_count:
      why = why.decode('utf-8')
      for _ in range(3):
        max_len = 60  # in a LINE message
        msgs.append({
            'text': why[:max_len],
        })
        why = why[max_len:]
        if not why:
          break
    else:
      pass  # Don't show anything if user dislikes everything.
    """

    return {
      'messages': msgs,
    }

  def GetReasons(self):
    """Get recommendation reasons.

    Args:
      Common:
        user_lang=zh_TW
        selected=["+羊肉爐", "+漢堡", "+洋蔥", "+肉圓", "+豆腐鍋"]
      Web:
        local_langs=[["zh_TW", 1.0]]
      Comopse.ai:
        location={u'coordinates': {u'lat': 25.0339031, u'long': 121.5645099}}
        platform_user_ident=1115862448503460

    Returns:
      list of a dict:
    """
    selected = json.loads(self.request.get("selected"))
    user_lang = self.request.get("user_lang")

    logging.debug('selected: %r', selected)
    logging.debug('user_lang: %r', user_lang)

    msgs = []
    like_count = 0
    for person in selected:
      if person.startswith('+'):
        like_count += 1
        name = person[1:].encode('utf-8')
        intro = people.data[name]['desc']
        msgs.append({
            'text': name + '：' + intro + '。',
        })

    if not like_count:
      msgs.append({
          'text': '你沒有喜歡的名人，所以我自己找了一些基金給你。',
      })

    return {
      'messages': msgs,
    }

  def GetPreference(self):
    """Get preference for compose.ai bot.

    Args:
      platform_user_ident=1115862448503460
      timezone=-8

    Returns:
      dict = {
        'memory': {
          'search_radius': nnnn,  # unit: meter
        }
      }
    """
    # TODO: move to want.py or any file else for better unit testing.

    timezone = float(self.request.get('timezone'))
    local_dt = (datetime.datetime.utcnow() +
                datetime.timedelta(0, timezone * 3600))

    if local_dt.weekday() in [5, 6]:  # Sat and Sun
      search_radius = 40 * 1000  # weekend: 40km
    else:
      # weekday
      hour = local_dt.time().hour
      if hour >= 10 and hour <= 13:
        search_radius = 12 * 1000  # lunch: 1.2km
      elif hour >= 15 and hour <= 20:
        search_radius = 10 * 1000  # dinner: 10km
      else:
        search_radius = 20 * 1000  # other: 20km

    return {
      'memory': {
        'search_radius': search_radius,
      }
    }

  def RecordSelectedFoods(self):
    """Record down the foods user selected.

    Args:
      user_lang: string. Can be 'xx_YY' or 'xx-YY'.
      selected: JSON string. Ex: ["+羊肉爐", "+漢堡", "+洋蔥", "+肉圓"]
      platform_user_ident: string. Ex: '1115862448503460'
    """
    user_lang = self.request.get('user_lang')
    selected = json.loads(self.request.get('selected'))
    platform_user_ident = self.request.get('platform_user_ident')

    return want.RecordSelectedFoods(user_lang, selected, platform_user_ident)

  def NextFoodsToChoose(self):
    """Returns five foods for user to choose.

    Args:
      input: A JSON string. Ex: [] or ["+羊肉爐", "+漢堡", "+洋蔥", "+肉圓"]
      hl: string. Ex: 'zh-TW'
      platform_user_ident: string. Ex: '1115862448503460'

    Returns:
      array of dict {'food': fund_name}
    """
    input = json.loads(self.request.get("input"))
    hl = self.request.get("hl")
    platform_user_ident = self.request.get('platform_user_ident')
    next = want.next_foods_to_choose(input, hl, platform_user_ident)

    # random the weighted order in the server side.
    for n in next:
      n["score"] = n["score"] * random.random()
    next = sorted(next,
                  cmp = lambda x, y: int((y["score"] - x["score"]) * 10000))

    # remove score before sending to client.
    for n in next:
      del n["score"]

    return next[:5]

  def KeywordQuery(self):
    """Use keyword to query most relative funds.

    Args:
      user_lang: string. Can be 'xx_YY' or 'xx-YY'
      keyword: string. Keyword use to query. Can be multiple separated by spaces

    Returns:
      Commando format.
    """
    user_lang = self.request.get('user_lang')
    keyword = self.request.get('keyword')

    funds = want.KeywordQuery(user_lang, keyword)

    msgs = []

    elements = []
    for f in funds[:3]:
      elements.append({
          'image_url': f['image_url'],
          'item_url': f['item_url'],
          'title': f['display_name'],
          'subtitle': f['desc'],
          'buttons': [{
            'type': 'web_url',
            'title': '基金介紹',
            'url': f['item_url'],
          }],
      })

    if elements:
      msgs.append({
          'text': u'以下是使用關鍵字「%s」搜尋的基金:：' % keyword,
      })
      msgs.append({
          'attachment': {
              'type': 'template',
              'payload': {
                  'template_type': 'generic',
                  'elements': elements,
              },
          }
      })
    else:
      msgs.append({
          'text': u'找不到「%s」相關的基金:：' % keyword,
      })

    return {
      'messages': msgs,
    }

  def ListCategory(self):
    """Get a random list from category.

    Args:
      category: one of 債券型, 股票型, 平衡型

    Returns:
      Commando format.
    """
    category = self.request.get('category')
    funds = want.ListCategory(category)

    msgs = []

    elements = []
    random.shuffle(funds)
    for f in funds[:3]:
      elements.append({
          'image_url': f['image_url'],
          'item_url': f['item_url'],
          'title': f['display_name'],
          'subtitle': f['desc'],
          'buttons': [{
            'type': 'web_url',
            'title': '基金介紹',
            'url': f['item_url'],
          }],
      })

    if elements:
      msgs.append({
          'text': u'你可能會喜歡的「%s」基金： 💋 ' % category,
      })
      msgs.append({
          'attachment': {
              'type': 'template',
              'payload': {
                  'template_type': 'generic',
                  'elements': elements,
              },
          }
      })
    else:
      msgs.append({
          'text': u'找不到「%s」相關的基金:：' % category,
      })

    return {
      'messages': msgs,
    }
