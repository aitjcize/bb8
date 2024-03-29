#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TW Real Price Unittest"""

import datetime
import unittest

import twrealprice_rule


class TestRule(unittest.TestCase):
    def setUp(self):
        self.rule = twrealprice_rule.Rule(
            parse_query=lambda query: u'套房' in query,
            count_score=lambda tran: (
                1.0 if '套房' in tran['建物型態'] else -1.0))

    def test_parse(self):
        self.assertEqual(bool(self.rule.ParseQuery(u'XX套房XX')), True)

    def test_score(self):
        self.assertGreater(self.rule.CountScore(
            {'建物型態': '套房(1房1廳1衛)'}), 0)
        self.assertLess(self.rule.CountScore(
            {'建物型態': '公寓(5樓含以下無電梯)'}), 0)


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = twrealprice_rule.Matcher(
            accept_words=[u'透天', u'整棟'],
            tran_key='建物型態',
            tran_value='透天厝',
            weight=1000)

    def test_parser(self):
        self.assertTrue(self.matcher.ParseQuery(query=u'我想買透天厝'))
        self.assertTrue(self.matcher.ParseQuery(query=u'我想買整棟的'))

    def test_score(self):
        self.assertGreater(self.matcher.CountScore({'建物型態': '透天厝'}), 0)


class TestNumber(unittest.TestCase):
    def setUp(self):
        self.integer = twrealprice_rule.Number(
            unit=u'樓',
            tran_key='移轉層次',
            weight=10)
        self.float = twrealprice_rule.Number(
            unit=u'坪',
            tran_key='建物移轉總面積平方公尺',
            weight=10,
            scale=3.3)
        self.room = twrealprice_rule.Number(
            unit=u'房',
            tran_key='建物現況格局-房',
            weight=10)  # To regress slope=1.0 and scale=1.0

    def test_integer(self):
        self.assertTrue(self.integer.ParseQuery(query=u'我想買5樓'))
        self.assertEqual(self.integer.CountScore({'移轉層次': '五層'}), 1.0)

    def test_ping(self):
        self.assertTrue(self.float.ParseQuery(query=u'室內19.23坪'))
        self.assertAlmostEqual(self.float.CountScore(
            {'建物移轉總面積平方公尺': '63.459'}), 1.0)

    def test_room(self):
        self.assertTrue(self.room.ParseQuery(query=u'2房'))
        self.assertAlmostEqual(self.room.CountScore(
            {'建物現況格局-房': '2'}), 1.0)
        self.assertAlmostEqual(self.room.CountScore(
            {'建物現況格局-房': '3'}), 0.0)


class TestDays(unittest.TestCase):
    def setUp(self):
        self.trading = twrealprice_rule.Days(
            weight=10.0, tran_key='交易年月日')
        self.latest = twrealprice_rule.Days(
            weight=500.0, tran_key='交易年月日', accept_words=[u'最近'])
        self.trading.today = datetime.date(2011, 12, 13)

    def test_days(self):
        self.assertEqual(self.trading.CountScore(
            {'交易年月日': '1001213'}), 1.0)
        self.assertEqual(self.trading.CountScore(
            {'交易年月日': '991213'}), 0.0)

        self.assertEqual(self.latest.ParseQuery(u'X最近Y'), True)
        self.assertEqual(self.latest.Eliminate(u'XX最近YY'), u'XXYY')


class TestLocation(unittest.TestCase):
    def setUp(self):
        self.location = twrealprice_rule.Location(
            weight=10.0,
            tran_key='latlng', latlng=(25.0554948, 121.6004863))

    def test_days(self):
        self.assertEqual(self.location.CountScore(
            {'latlng': (25.0554948, 121.6004863)}), 1.0)
        self.assertAlmostEqual(self.location.CountScore(
            {'latlng': (25.0557478, 121.6030973)}), 0.47535421473121797)


class TestPrice(unittest.TestCase):
    def setUp(self):
        self.price = twrealprice_rule.Number(
            weight=10.0, unit=u'萬', tran_key='總價元', slope=-0.2, scale=10000)

    def test_price(self):
        self.assertTrue(self.price.ParseQuery(query=u'1000.0萬'))
        self.assertEqual(self.price.CountScore({'總價元': '10000000'}), 1.0)
        self.assertTrue(self.price.ParseQuery(query=u'100萬'))
        self.assertEqual(self.price.CountScore({'總價元': '900000'}), 0.5)
        self.assertTrue(self.price.ParseQuery(query=u'10萬'))
        self.assertEqual(self.price.CountScore({'總價元': '110000'}), 0.5)


class TestRules(unittest.TestCase):
    def setUp(self):
        self.rules = twrealprice_rule.Rules()
        self.rules.Add(twrealprice_rule.Matcher(
            weight=1000,
            accept_words=[u'透天', u'獨棟'], tran_key='建物型態',
            tran_value='透天'))

    def test_single(self):
        self.rules.ParseQuery(u'爺們兒只買獨棟別墅')
        self.rules.CountScore([
            {'建物型態': '公寓'},
            {'建物型態': '透天厝'},
        ])
        self.rules.Sort()
        top = self.rules.Top(10)
        self.assertEqual(top[0]['建物型態'], '透天厝')


class TestCanonize(unittest.TestCase):
    def setUp(self):
        self.rules = twrealprice_rule.Rules.Create()
        self.canonizer = self.rules.Canonize

    def test_numbers(self):
        self.assertEqual(self.canonizer(u'五十六'), u'56')
        self.assertEqual(self.canonizer(u'五十'), u'50')
        self.assertEqual(self.canonizer(u'十六'), u'16')
        self.assertEqual(self.canonizer(u'一十六'), u'16')
        self.assertEqual(self.canonizer(u'十'), u'10')
        self.assertEqual(self.canonizer(u'一'), u'1')
        self.assertEqual(self.canonizer(u'一千二百一十六'), u'1216')
        self.assertEqual(self.canonizer(u'九千零三十'), u'9030')
        self.assertEqual(self.canonizer(u'１９７８'), u'1978')
        self.assertEqual(self.canonizer(u'叁層'), u'3樓')
        self.assertEqual(self.canonizer(u'三十坪'), u'30坪')

        self.assertEqual(self.canonizer(u'十萬'), u'10萬')
        self.assertEqual(self.canonizer(u'一千五百萬'), u'1500萬')
        self.assertEqual(self.canonizer(u'一千五百六十八萬'), u'1568萬')
        self.assertEqual(self.canonizer(u'一億'), u'10000萬')
        self.assertEqual(self.canonizer(u'一億一千五百萬'), u'11500萬')
        self.assertEqual(self.canonizer(u'二億'), u'20000萬')
        self.assertEqual(self.canonizer(u'二億五千一百萬'), u'25100萬')
        self.assertEqual(self.canonizer(
            u'二十三億五千一百六十八萬'), u'235168萬')

        units = self.rules.units
        self.assertEqual(self.canonizer(u'三十坪', units=units), u'30坪')
        self.assertEqual(self.canonizer(u'十六坪', units=units), u'16坪')
        self.assertEqual(self.canonizer(u'三十六坪', units=units), u'36坪')
        self.assertEqual(self.canonizer(u'十坪', units=units), u'10坪')
        self.assertEqual(
            self.canonizer(
                u'五結鄉親河路二段', units=units),
            u'五結鄉親河路二段')
        self.assertEqual(
            self.canonizer(
                u'大墩十二街', units=units),
            u'大墩十二街')
        self.assertEqual(
            self.canonizer(
                u'十信高中', units=units),
            u'十信高中')
        self.assertEqual(
            self.canonizer(
                u'十全十美', units=units),
            u'十全十美')
        self.assertEqual(
            self.canonizer(
                u'新竹縣竹北市六家一路一段27號', units=units),
            u'新竹縣竹北市六家一路一段27號')
        self.assertEqual(
            self.canonizer(
                u'雙十路', units=units),
            u'雙十路')
        self.assertEqual(
            self.canonizer(
                u'三二行館', units=units),
            u'三二行館')
        self.assertEqual(
            self.canonizer(
                u'四十八章', units=units),
            u'四十八章')
        self.assertEqual(
            self.canonizer(
                u'七十巷', units=units),
            u'七十巷')
        self.assertEqual(
            self.canonizer(
                u'七十七巷', units=units),
            u'七十七巷')
        self.assertEqual(
            self.canonizer(
                u'十巷', units=units),
            u'十巷')
        self.assertEqual(
            self.canonizer(
                u'七巷', units=units),
            u'七巷')


if __name__ == "__main__":
    unittest.main()
