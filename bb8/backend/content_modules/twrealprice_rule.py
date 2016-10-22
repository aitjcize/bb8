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


# Square meter of a ping
M2_PER_PING = 3.3


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
        self.for_sort_only = False

    def ParseQuery(self, query):
        """Parse user's query and return whether matched or not.

        Args:
          query: str. user's query. contains keywords.

        Returns:
          not None: means this rule is matched.
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
        self.matched = None

    def ParseQuery(self, query):
        for word in self.accept_words:
            if word in query:
                self.matched = word
                return True
        return False

    def Eliminate(self, query):
        return query.replace(self.matched, '', 1)

    def CountScore(self, tran):
        return 1.0 if self.tran_value in tran[self.tran_key] else 0

    def __str__(self):
        return self.tran_value.decode('utf-8')


class Number(Rule):
    def __init__(self, unit, tran_key, weight, scale=1.0, slope=1.0):
        """A number with unit.

        Args:
          unit: str. The unit name.
          tran_key: the key of transaction to search number.
          weight: weight for this score.
          scale: the scale factor to apply on the number in the user's query.
          slope: the slope ratio used in count score.
        """
        super(Number, self).__init__(weight=weight)
        self.unit = unit
        self.tran_key = tran_key
        self.scale = scale
        self.slope = slope

        # The variables will be set later
        self.number = None
        self.sorted = None
        self.scores = None
        self.matched = None

    def ParseQuery(self, query):
        m = re.search(ur'(([0-9]+(\.[0-9]+)?)\s*' + self.unit + ')', query)
        if m:
            self.matched = m.group(1)
            self.number = float(m.group(2))
            return True
        return False

    def Eliminate(self, query):
        return query.replace(self.matched, '', 1)

    def CountScore(self, tran):
        """Linear function to get the score.

        if slope < 0: is percentage of the query.
                 > 0: same unit as query.

        score = (delta / slope)  if 0 <= delta <= slope
              = 1.0              if delta > slope

        Args:
          tran: dict. transaction data.

        Returns:
          float. scores
        """
        m = re.search(r'([0-9]+(\.[0-9]+)?)',
                      Rules.Canonize(tran[self.tran_key].decode('utf-8')))

        query_number = self.number * self.scale

        if self.slope < 0:
            slope = float(query_number) * -self.slope
        else:
            slope = self.slope

        if m:
            diff = math.fabs(query_number - float(m.group(1)))
            return 1.0 - max(0, min(1.0, diff / slope))
        else:
            return 0.0

    def __str__(self):
        return u'%s%s' % (self.number, self.unit)


class Days(Rule):
    def __init__(self, tran_key, weight):
        """Used to count days. Higher score for closer date.

        Args:
          tran_key: the key of transaction to search number.
          weight: weight for this score.
        """
        super(Days, self).__init__(weight=weight)
        self.for_sort_only = True
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
        return u''


class Location(Rule):
    def __init__(self, tran_key, latlng, weight):
        """Used to sort distance. Closer location has higher score.

        Args:
          tran_key: the key of transaction to search number.
          latlng: (lat, lng). the center lat/lng.
          weight: weight for this score.
        """
        super(Location, self).__init__(weight=weight)
        self.for_sort_only = True
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
        # 0.0: ~500m
        return max(0, min(1.0, 1.0 - distance / 0.005))

    def __str__(self):
        return u''


class Rules(object):
    def __init__(self):
        """Collection of rules."""
        self.rules = []
        self.sorted = None
        self.scores = None
        self.matched = []

    def Add(self, rule):
        self.rules.append(rule)

    @property
    def units(self):
        return ''.join([r.unit for r in self.rules if hasattr(r, 'unit')])

    def ParseQuery(self, query):
        """Parse user's query and collect matched rules internally.

        Results saved in self.matched.

        Args:
          query: unicode str.

        Returns:
          unicode str: the remaining string after eliminating matched rules.
        """
        query = self.Canonize(query, units=self.units)
        for r in self.rules:
            if r.ParseQuery(query):
                self.matched.append(r)

        for m in self.matched:
            query = m.Eliminate(query)

        return query

    def AddPureSortingRules(self, latlng):
        self.matched.append(Days(weight=50, tran_key='交易年月日'))
        self.matched.append(Location(
            weight=300, tran_key='latlng', latlng=latlng))

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
        return [u'%s' % m for m in self.matched if not m.for_sort_only]

    @classmethod
    def Canonize(cls, query, units=None):
        """Canonize user's query before parse.

        Including:
          - 層 --> 樓
          - Chinese number to Arabic number

        Due to RE match issue, convert to unicode while processing.

        Args:
          query: Unicode str.

        Returns:
          Unicode str: canonized str
        """
        query = query.replace(u'層', u'樓')

        nums = {
            u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5,
            u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'兩': 2,
            u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4,
            u'５': 5, u'６': 6, u'７': 7, u'８': 8, u'９': 9,
            u'零': 0, u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4,
            u'伍': 5, u'陸': 6, u'柒': 7, u'捌': 8, u'玖': 9,
        }

        # Split into 2 parts: larther than and less than 億.
        # So that 二億五千一百萬 ==> 25100萬
        query = re.sub(
            ur'([0123456789一二三四五六七八九])億', ur'\g<1>==YI==', query)
        yis = re.split(ur'==YI==', query)

        ret = u''
        for query in yis:
            query = re.sub(ur'([一二三四五六七八九])千萬', ur'\g<1>000萬', query)
            query = re.sub(ur'([一二三四五六七八九])千', ur'\1', query)
            query = re.sub(ur'([一二三四五六七八九])百萬', ur'\g<1>00萬', query)
            query = re.sub(ur'([一二三四五六七八九])百', ur'\1', query)
            query = re.sub(ur'([一二三四五六七八九])十([一二三四五六七八九])',
                           ur'\1__MIDTEN__\2', query)  # 五十六 --> 五六
            query = re.sub(ur'([一二三四五六七八九])十',
                           ur'\g<1>__TENS__', query)  # 七十 --> 七__TENS__
            query = re.sub(ur'十([一二三四五六七八九])',
                           ur'__TENTH__\1', query)  # 十八 --> __TENTH__八
            query = query.replace(u'十', u'__TEN__')  # 十 --> __TEN__

            # At final, convert chinese numbers: 五六-->56
            if units:
                # Only convert chinese numbers right before unit
                for _ in range(len(query)):
                    org = query

                    for chinese_num, arabic_num in nums.iteritems():
                        query = re.sub(
                            ur'%s([\d%s])' % (chinese_num, units),
                            ur'%s\g<1>' % arabic_num,
                            query)
                        query = re.sub(ur'__MIDTEN__([\d])', ur'\g<1>', query)
                        query = re.sub(ur'__TENTH__([\d])', ur'1\g<1>', query)
                        query = re.sub(
                            ur'__TENS__([%s])' % units, ur'0\g<1>', query)
                        query = re.sub(
                            ur'__TEN__([%s])' % units, ur'10\g<1>', query)

                    if org == query:
                        break

                # If those special numbers cannot be converted, that must be
                # not something with units, convert it back.
                query = query.replace(ur'__MIDTEN__', u'十')
                query = query.replace(ur'__TENTH__', u'十')
                query = query.replace(ur'__TEN__', u'十')

            else:
                # not units
                for chinese_num, arabic_num in nums.iteritems():
                    query = query.replace(chinese_num, unicode(arabic_num))

                query = query.replace(ur'__MIDTEN__', u'')
                query = query.replace(ur'__TENS__', u'0')
                query = re.sub(ur'__TENTH__', ur'1', query)
                query = query.replace(ur'__TEN__', u'10')

            if re.search(ur'__.*TEN.*__', query):
                raise RuntimeError('Not convert it back: %s' % query)

            if not query:
                query = u'0000萬'

            ret = ret + query

        return ret

    @classmethod
    def Create(cls):
        rules = cls()

        # Building types
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'套房'], tran_key='建物型態', tran_value='套房'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'公寓'], tran_key='建物型態', tran_value='公寓'))
        rules.Add(Matcher(  # Hack. Must be prior to 華廈.
            weight=1000,
            accept_words=[u'電梯大樓', u'住宅大樓', u'大樓'],
            tran_key='建物型態',
            tran_value='住宅大樓'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'電梯華廈', u'華廈', u'大樓'], tran_key='建物型態',
            tran_value='華廈'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'商辦', u'商業大樓'], tran_key='建物型態',
            tran_value='辦公商業大樓'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'透天厝', u'透天', u'獨棟', u'別墅', u'獨棟別墅'],
            tran_key='建物型態',
            tran_value='透天厝'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'農舍'], tran_key='建物型態', tran_value='農舍'))
        rules.Add(Matcher(
            weight=1000,
            accept_words=[u'店面'], tran_key='建物型態', tran_value='店面'))

        # Numbers
        rules.Add(Number(weight=150, unit=u'年', tran_key='AGE', slope=10.0))
        rules.Add(Number(
            weight=250, unit=u'坪', slope=20 * M2_PER_PING,
            tran_key='建物移轉總面積平方公尺', scale=M2_PER_PING))
        rules.Add(Number(weight=100, unit=u'樓', tran_key='移轉層次', slope=4))
        rules.Add(Number(
            weight=200, unit=u'萬', tran_key='總價元', slope=-0.2, scale=10000))
        rules.Add(Number(
            weight=400, unit=u'房', tran_key='建物現況格局-房',
            slope=1.0, scale=1.0))
        rules.Add(Number(
            weight=150, unit=u'廳', tran_key='建物現況格局-廳',
            slope=1.0, scale=1.0))
        rules.Add(Number(
            weight=150, unit=u'衛', tran_key='建物現況格局-衛',
            slope=1.0, scale=1.0))

        return rules
