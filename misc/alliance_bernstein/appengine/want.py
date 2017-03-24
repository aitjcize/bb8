#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is to serve the logic for want_ajax.py by using the data from
food.py.
"""

import logging

import alliance_bernstein
import fund
import gram
import people
import user
import utils

def IndexFunds(funds):
  """Generate the index for all funds.

  Args:
    funds: dict of fund. Typically, the fund.data

  Returns:
    gram.Documnets.
  """
  docs = []

  for fund_name, fund in funds.iteritems():
    keywords = fund['keywords'].split(',')
    docs.append(
        gram.Document(
            void_p=fund,
            bigram_dict=gram.BigramDict.FromStringList(keywords)))

  return gram.Documents(docs)

def get_recommended_foods(input, user_lang, local_langs):
  """Returns foods for user to eat.

  Args:
    input: list of str. ['+food1', '-food2'] (Unicode)
    user_lang: str. User's locale. zh-TW or zh_TW
    local_langs: list of [locale, score]. Local locale for local search.

  Returns:
    array of dict {'food': fund_name, 'score': XXX.XXX}
  """
  assert len(input) > 0

  scores = {k: 0.0 for k in fund.data.keys()}

  # Convert getLangs() structure to dict:
  #   [["zh-TW", 1.0], ["en-US", 0.1]];
  #   -->
  #   {'zh-TW': 1.0, 'en-US': 0.1}
  #
  # TODO: move definitions from s/js/map.js:getLangs() to here.
  local_langs = {utils.canonize_locale(k): v for (k, v) in local_langs}
  logging.debug('local_lang: %r', local_langs)

  user_lang = utils.canonize_locale(user_lang)
  logging.debug('user_lang: %s', user_lang)

  for inp in input:
    # get weight
    if inp[0] == u"+":
      weight = 1.0
    elif inp[0] == u"-":
      weight = -1.0
    else:
      raise ValueError('Unknown input: %s' % inp)
    logging.debug('inp[%s]: %1.2f', inp, weight)
    inp = inp[1:].encode('utf-8')

    likes = alliance_bernstein.data[inp]
    for fund_name, score in likes.iteritems():
      if score == '':
        score = 0.0
      scores[fund_name] += score * weight

  # sort before return.
  sorted_scores = [{"food": x, "score": scores[x]} for x in scores]
  sorted_scores = sorted(sorted_scores,
      # the compare function only accept int, rather than float
      cmp = lambda x, y: int((y["score"] - x["score"]) * 1000000))

  return sorted_scores

def RecordSelectedFoods(user_lang, selected, platform_user_ident):
  """Record down the foods user selected.

  Args:
    user_lang: string. Can be 'xx_YY' or 'xx-YY'.
    selected: JSON string. Ex: ["+羊肉爐", "+漢堡", "+洋蔥", "+肉圓"]
    platform_user_ident: string. Ex: '1115862448503460'
  """
  diet_habit = user.GetUserParameter(
      uid=platform_user_ident,
      cls=user.DietHabit)
  selected = [(x[0] == '+', x[1:]) for x in selected]
  return diet_habit.Update(selected)

def next_foods_to_choose(input, lang, platform_user_ident=None):
  """Returns an array for user's questionaire.

  Args:
    lang: locale. Can be 'xx_YY' or 'xx-YY'.

  Returns:
    array of dict {'food': celebrity name, 'score': x.x}
  """
  lang = utils.canonize_locale(lang)

  celebrity = people.intro.keys()

  if not celebrity:
    raise Exception('No celebrity in language: %s' % lang)

  # Load user's diet habit (if applicable)
  if platform_user_ident:
    diet_habit = user.GetUserParameter(
        uid=platform_user_ident,
        cls=user.DietHabit)
  else:
    class MockDietHabit(object):
      def GetScore(self, unused_foodname):
        return 1.0
    diet_habit = MockDietHabit()

  return [{'food': name, 'score': 1.0} for name in celebrity]

def KeywordQuery(user_lang, keyword):
  """Use keyword to query most relative funds.

  Args:
    user_lang: string. Can be 'xx_YY' or 'xx-YY'
    keyword: string. Keyword use to query. Can be multiple separated by spaces

  Returns:
    list of fund.data element.
  """
  bigram_dict = gram.BigramDict.FromString(keyword)
  docs = fund_index.Search(bigram_dict)
  return [x.void_p for x in docs if x.score > 0]


# Global variable. Load once.
fund_index = IndexFunds(fund.data)
