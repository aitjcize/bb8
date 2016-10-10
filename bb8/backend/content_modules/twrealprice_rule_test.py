#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TW Real Price Unittest"""

import datetime
import unittest

import twrealprice_rule


class TestRule(unittest.TestCase):
    def setUp(self):
        self.rule = twrealprice_rule.Rule(
            parse_query=lambda query: '套房' in query,
            count_score=lambda tran: (
                1.0 if '套房' in tran['建物型態'] else -1.0))

    def test_parse(self):
        self.assertEqual(bool(self.rule.ParseQuery('XX套房XX')), True)

    def test_score(self):
        self.assertGreater(self.rule.CountScore(
            {'建物型態': '套房(1房1廳1衛)'}), 0)
        self.assertLess(self.rule.CountScore(
            {'建物型態': '公寓(5樓含以下無電梯)'}), 0)


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = twrealprice_rule.Matcher(
            accept_words=['透天', '整棟'],
            tran_key='建物型態',
            tran_value='透天厝',
            weight=1000)

    def test_parser(self):
        self.assertTrue(self.matcher.ParseQuery(query='我想買透天厝'))
        self.assertTrue(self.matcher.ParseQuery(query='我想買整棟的'))

    def test_score(self):
        self.assertGreater(self.matcher.CountScore({'建物型態': '透天厝'}), 0)


class TestNumber(unittest.TestCase):
    def setUp(self):
        self.integer = twrealprice_rule.Number(
            unit='樓',
            tran_key='移轉層次',
            weight=10)
        self.float = twrealprice_rule.Number(
            unit='坪',
            tran_key='建物移轉總面積平方公尺',
            weight=10,
            scale=3.3)

    def test_integer(self):
        self.assertTrue(self.integer.ParseQuery(query='我想買5樓'))
        self.assertEqual(self.integer.CountScore({'移轉層次': '五層'}), 1.0)

    def test_ping(self):
        self.assertTrue(self.float.ParseQuery(query='室內19.23坪'))
        self.assertAlmostEqual(self.float.CountScore(
            {'建物移轉總面積平方公尺': '63.459'}), 1.0)


class TestDays(unittest.TestCase):
    def setUp(self):
        self.trading = twrealprice_rule.Days(
            weight=10.0, tran_key='交易年月日')
        self.trading.today = datetime.date(2011, 12, 13)

    def test_days(self):
        self.assertEqual(self.trading.CountScore(
            {'交易年月日': '1001213'}), 1.0)
        self.assertEqual(self.trading.CountScore(
            {'交易年月日': '991213'}), 0.0)


class TestLocation(unittest.TestCase):
    def setUp(self):
        self.location = twrealprice_rule.Location(
            weight=10.0,
            tran_key='latlng', latlng=(25.0554948, 121.6004863))

    def test_days(self):
        self.assertEqual(self.location.CountScore(
            {'latlng': (25.0554948, 121.6004863)}), 1.0)
        self.assertAlmostEqual(self.location.CountScore(
            {'latlng': (25.0557478, 121.6060973)}), 0.43832990109835046)


class TestRules(unittest.TestCase):
    def setUp(self):
        self.rules = twrealprice_rule.Rules()
        self.rules.Add(twrealprice_rule.Matcher(
            weight=1000,
            accept_words=['透天', '獨棟'], tran_key='建物型態',
            tran_value='透天'))

    def test_single(self):
        self.rules.ParseQuery('爺們兒只買獨棟別墅')
        self.rules.CountScore([
            {'建物型態': '公寓'},
            {'建物型態': '透天厝'},
        ])
        self.rules.Sort()
        top = self.rules.Top(10)
        self.assertEqual(top[0]['建物型態'], '透天厝')


class TestCanonize(unittest.TestCase):
    def setUp(self):
        self.canonizer = twrealprice_rule.Rules.Canonize

    def test_numbers(self):
        self.assertEqual(self.canonizer('五十六'), '56')
        self.assertEqual(self.canonizer('五十'), '50')
        self.assertEqual(self.canonizer('十六'), '16')
        self.assertEqual(self.canonizer('一十六'), '16')
        self.assertEqual(self.canonizer('十'), '10')
        self.assertEqual(self.canonizer('一千二百一十六'), '1216')
        self.assertEqual(self.canonizer('九千零三十'), '9030')
        self.assertEqual(self.canonizer('１９７８'), '1978')
        self.assertEqual(self.canonizer('叁層'), '3樓')
        self.assertEqual(self.canonizer('三十坪'), '30坪')

if __name__ == "__main__":
    unittest.main()
