#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import gram

class TestGram(unittest.TestCase):
  def setUp(self):
    pass

  def test_normal(self):
    self.assertEqual(
        gram.Grams.FromString(',ab, d '),
        gram.Grams([
            gram.Gram(u'ab'),
            gram.Gram(u'd'),
        ])
    )

    self.assertEqual(
        gram.Grams.FromString(' 狗屎ab狗屎, 狗d e屎 '),
        gram.Grams([
            gram.Gram(u'狗'),
            gram.Gram(u'屎'),
            gram.Gram(u'ab'),
            gram.Gram(u'狗'),
            gram.Gram(u'屎'),
            gram.Gram(u'狗'),
            gram.Gram(u'd'),
            gram.Gram(u'e'),
            gram.Gram(u'屎'),
        ])
    )


class TestBigramDict(unittest.TestCase):
  def test_normal(self):
    actual = gram.BigramDict.FromStringList(['之中出', '中出了'])
    expect = gram.BigramDict.FromBigrams([
        gram.Bigram([gram.Gram(u'之'), gram.Gram(u'中')]),
        gram.Bigram([gram.Gram(u'中'), gram.Gram(u'出')]),
        gram.Bigram([gram.Gram(u'中'), gram.Gram(u'出')]),
        gram.Bigram([gram.Gram(u'出'), gram.Gram(u'了')]),
    ])
    self.assertEqual(
        actual, expect,
        msg='{0}, {1}'.format(actual, expect)
    )


class TestDocuments(unittest.TestCase):
  def setUp(self):
    self.us_debit_ = gram.Document(
        'US_DEBIT', gram.BigramDict.FromString('美國收益基金'))
    self.us_hitech_ = gram.Document(
        'US_HITECH', gram.BigramDict.FromString('美國高科技基金'))
    self.new_tech = gram.Document(
        'NEW_TECH', gram.BigramDict.FromString('新科技基金'))

    self.docs_ = gram.Documents([
        self.us_debit_,
        self.us_hitech_,
        self.new_tech,
    ])

  def test_normal(self):
    hi_tech = [x.void_p for x in self.docs_.Search(gram.BigramDict.FromString('高科技'))]
    expect = [x.void_p for x in [self.us_hitech_, self.new_tech, self.us_debit_]]
    self.assertEqual(hi_tech, expect,
        msg='{0}, {1}'.format(hi_tech, expect))

if __name__ == '__main__':
  unittest.main()
