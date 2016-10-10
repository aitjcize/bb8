#!/usr/bin/env python
# -*- coding: utf-8 -*-o
"""This module is used to provide filter/sorting features for search results.

  1. User enters some key words or criteria to tell what kind of objects they
     are interested in. E.g. '四十坪公寓' or '10年大樓'.

  2. This query will go through all rules from Create() below.

  3. For those matched rules, ParseQuery will return True.

  4. Those are rules will be collected in Rules object.

  5. Then, search all nearby transactions with those matched rules.

  6. Every rule will return a score (and weight).

  7. Get a summed score for each transaction.

  8. Sort by score, then return the top N results back.

Because I am lazy, all funtions in this file accept 'UTF-8' encoding string.
"""

# pylint: disable=E0202

import copy
import datetime
import math
import re


def AdDate(roc_date):
    """Convert ROC date string to AD date.

    Args:
      roc_date: 7-digit, e.g. 1050723 or 990102

    Returns:
      datetime.date
    """
    if len(roc_date) == 7:
        roc = (int(roc_date[0:3]) + 1911,
               int(roc_date[3:5]),
               int(roc_date[5:]))
    elif len(roc_date) == 6:
        roc = (int(roc_date[0:2]) + 1911,
               int(roc_date[2:4]),
               int(roc_date[4:]))
    else:
        raise ValueError('Invalid ROC date string: [%s]' % roc_date)

    return datetime.date(*roc)


class Rule(object):
    def __init__(self, parse_query=None, count_score=None, weight=1.0):
        """Constructor

        Args:
          parse_query: callback used in user's query.
          count_score: callabck used to score the transaction.
        """
        if parse_query:
            self.ParseQuery = parse_query
        if count_score:
            self.CountScore = count_score

        self.weight = weight

    def ParseQuery(self, query):
        """Parse user's query and return whether matched or not.

        Args:
          query: str. user's query. contains keywords.

        Returns:
          Anything not None: means this rule is matched.
        """
        raise NotImplementedError

    def CountScore(self, transaction):
        """Calculate score of a transaction.

        Args:
          transcaction: dict. One transaction data.

        Returns:
          float. The computed score for sorting.
        """
        raise NotImplementedError

    def __str__(self):
        """Used to prompt user what the criteria is"""
        raise NotImplementedError


class Matcher(Rule):
    def __init__(self, accept_words, tran_key, tran_value, weight):
        """Boolean rule.

        Args:
          accept_words: str[]. The words to match in user's query.
                               This is how people would query.
          tran_key: the key of transaction to match.
          tran_value: the value to match.
          weight: weight for this score.
        """
        super(Matcher, self).__init__(weight=weight)
        self.accept_words = accept_words
        self.tran_key = tran_key
        self.tran_value = tran_value

    def ParseQuery(self, query):
        for word in self.accept_words:
            if word in query:
                return True
        return False

    def CountScore(self, tran):
        return 1.0 if self.tran_value in tran[self.tran_key] else 0

    def __str__(self):
        return '%s' % self.tran_value


class Number(Rule):
    def __init__(self, unit, tran_key, weight, scale=1.0):
        """A number with unit.

        Args:
          unit: str. The unit name.
          tran_key: the key of transaction to search number.
          weight: weight for this score.
          scale: the scale factor to apply on the number in the user's query.
        """
        super(Number, self).__init__(weight=weight)
        self.unit = unit
        self.tran_key = tran_key
        self.scale = scale

        # The variables will be set later
        self.number = None
        self.sorted = None
        self.scores = None
        self.matched = None

    def ParseQuery(self, query):
        m = re.search(r'([0-9]+(\.[0-9]+)?)\s*' + self.unit, query)
        if m:
            self.number = float(m.group(1))
            return True
        return False

    def CountScore(self, tran):
        m = re.search(r'([0-9]+(\.[0-9]+)?)',
                      Rules.Canonize(tran[self.tran_key]))
        if m:
            diff = math.fabs(self.number * self.scale - float(m.group(1)))
            diff = max(diff, 1)  # Saturated at 1.0
            return 1.0 * math.exp(-math.log(diff))
        else:
            return 0.0

    def __str__(self):
        return '%s%s' % (self.number, self.unit)


class Days(Rule):
    def __init__(self, tran_key, weight):
        """Used to count days. Higher score for closer date.

        Args:
          tran_key: the key of transaction to search number.
          weight: weight for this score.
        """
        super(Days, self).__init__(weight=weight)
        self.tran_key = tran_key
        self.today = datetime.date.today()

    def ParseQuery(self, query):
        return True  # Always matched. Used to sort the results.

    def CountScore(self, tran):
        try:
            delta = (self.today - AdDate(tran[self.tran_key])).days
        except ValueError:
            delta = 183  # half year

        # 1.0:   0 day  = up-to-date price!
        # 0.0: 365 days = the price year ago
        # 0.0: 366+days = older than 1 year
        return max(0, min(1.0, 1.0 - delta / 365))

    def __str__(self):
        return ''


class Location(Rule):
    def __init__(self, tran_key, latlng, weight):
        """Used to sort distance. Closer location has higher score.

        Args:
          tran_key: the key of transaction to search number.
          latlng: (lat, lng). the center lat/lng.
          weight: weight for this score.
        """
        super(Location, self).__init__(weight=weight)
        self.tran_key = tran_key
        self.latlng = latlng

    def ParseQuery(self, query):
        return True  # Always matched. Used to sort the results.

    def CountScore(self, tran):
        tran_lat, tran_lng = tran[self.tran_key]
        distance = math.sqrt(
            (tran_lat - self.latlng[0]) ** 2 +
            (tran_lng - self.latlng[1]) ** 2)

        # 1.0: at same location.
        # 0.0: ~1KM
        return max(0, min(1.0, 1.0 - distance / 0.01))

    def __str__(self):
        return ''


class Rules(object):
    def __init__(self):
        """Collection of rules."""
        self.rules = []
        self.sorted = None
        self.scores = None
        self.matched = None

    def Add(self, rule):
        self.rules.append(rule)

    def ParseQuery(self, query):
        """Parse user's query and collect matched rules internally.

        Results saved in self.matched.

        Args:
          query: utf-8 encoded str.
        """
        query = self.Canonize(query)
        self.matched = []
        for r in self.rules:
            if r.ParseQuery(query):
                self.matched.append(r)

    def CountScore(self, trans):
        """Count score of each transaction in trans.

        Results saved in self.scores -- with the key 'score'.

        Args:
          trans: array of dict.
        """
        self.scores = copy.copy(trans)

        for tran in self.scores:
            score = 0.0
            for m in self.matched:
                score += m.CountScore(tran) * m.weight
            tran['score'] = score

    def Sort(self):
        positive = [t for t in self.scores if t['score'] > 0]
        self.sorted = sorted(positive,
                             cmp=lambda a, b: cmp(b['score'], a['score']))

    def Top(self, n=None, start=0):
        """Return sorted results.

        Args:
          n: number to return. None means all.
          start: the start index to return.

        Returns:
          list of tran.
        """
        if n is None:
            return self.sorted
        else:
            return self.sorted[start:start+n]

    @property
    def filters(self):
        """Returns the list of human-readable filter used for count score"""
        return ['%s' % m for m in self.matched]

    @classmethod
    def Canonize(cls, query):
        """Canonize user's query before parse.

        Including:
          - 層 --> 樓
          - Chinese number to Arabic number

        Due to RE match issue, convert to unicode while processing.

        Args:
          query: utf-8 encoded str.

        Returns:
          str: canonized str
        """
        query = query.decode('utf-8')
        query = query.replace(u'層', u'樓')

        nums = {
            u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5,
            u'六': 6, u'七': 7, u'八': 8, u'九': 9,
            u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4,
            u'５': 5, u'６': 6, u'７': 7, u'８': 8, u'９': 9,
            u'零': 0, u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4,
            u'伍': 5, u'陸': 6, u'柒': 7, u'捌': 8, u'玖': 9,
        }
        query = re.sub(ur'([一二三四五六七八九])千', ur'\1', query)
        query = re.sub(ur'([一二三四五六七八九])百', ur'\1', query)
        query = re.sub(ur'([一二三四五六七八九])十([一二三四五六七八九])',
                       ur'\1\2', query)  # 五十六 --> 五六
        query = re.sub(ur'([一二三四五六七八九])十',
                       ur'\g<1>0', query)  # 七十 --> 七0
        query = re.sub(ur'十([一二三四五六七八九])',
                       ur'1\1', query)  # 十八 --> 1八
        query = query.replace(u'十', u'10')
        for chinese_num, arabic_num in nums.iteritems():
            query = query.replace(chinese_num, unicode(arabic_num))  # 五六-->56

        return query.encode('utf-8')

    @classmethod
    def Create(cls, latlng):
        rules = cls()

        # Building types
        rules.Add(Matcher(
            weight=1000,
            accept_words=['套房'], tran_key='建物型態', tran_value='套房'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['公寓'], tran_key='建物型態', tran_value='公寓'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['華廈', '大樓'], tran_key='建物型態',
            tran_value='華廈'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['大樓', '住宅大樓'], tran_key='建物型態',
            tran_value='住宅大樓'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['商辦', '商業大樓'], tran_key='建物型態',
            tran_value='辦公商業大樓'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['透天', '獨棟'], tran_key='建物型態',
            tran_value='透天厝'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['農舍'], tran_key='建物型態', tran_value='農舍'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=['店面'], tran_key='建物型態', tran_value='店面'))

        # Numbers
        rules.Add(Number(weight=200, unit='年', tran_key='AGE'))
        rules.Add(Number(
            weight=250, unit='坪',
            tran_key='建物移轉總面積平方公尺', scale=3.3))
        rules.Add(Number(weight=100, unit='樓', tran_key='移轉層次'))

        # Rules for sorting
        rules.Add(Days(weight=50, tran_key='交易年月日'))
        rules.Add(Location(weight=300, tran_key='latlng', latlng=latlng))

        return rules
