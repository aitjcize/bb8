# -*- coding: utf-8 -*-
"""Gram and bigram"""

import copy
import types

class Gram(object):
  def __init__(self, word):
    """Wrapper for a 'word' in all languages.

    Args:
      word: must be unicode
    """
    if type(word) != types.UnicodeType:
      raise ValueError('The string must be Unicode, actual: %s', type(string))

    self.word_ = word

  @property
  def word(self):
    return self.word_

  def __str__(self):
    return '<%s>' % self.word_.encode('utf-8')

  def __repr__(self):
    return self.__str__()

  def __hash__(self):
    return hash(self.word_)

  def __eq__(self, a):
    return self.word_ == a.word_

  def __ne__(self, a):
    return not (self == a)


class Grams(object):
  """Collection of gram"""
  @classmethod
  def FromString(cls, string):
    """Convert from the string.

    Args:
      string: utf-8 or unicode

    Returns:
      Grams instance
    """
    if type(string) == types.UnicodeType:
      pass
    elif type(string) == types.StringType:
      string = string.decode('utf-8')
    else:
      raise ValueError('Unsupported type: %r', type(string))

    grams = []
    cache = ''  # working buffer
    for ch in string:
      if ch == u' ' or ch == u',':
        if cache:
          grams.append(Gram(cache))
          cache = ''
      elif ord(ch) < 128:
        cache += ch
      else:  # ord(ch) >= 128
        if cache:
          grams.append(Gram(cache))
          cache = ''
        grams.append(Gram(ch))
    if cache:
      grams.append(Gram(cache))

    return cls(grams)

  def __init__(self, grams):
    """Constructor

    Args:
      grams: list of Gram.
    """
    self.grams_ = grams

  def __str__(self):
    return u'[' + ','.join(self.grams_) + ']'

  def __repr__(self):
    return self.__str__()

  def __eq__(self, a):
    return cmp(self.grams_, a.grams_) == 0

  def __ne__(self, a):
    return not (self == a)

  def __iter__(self):
    for gram in self.grams_:
      yield gram


class Bigram(object):
  def __init__(self, grams):
    if len(grams) != 2:
      raise ValueError('The # of grams is not 2: %r', grams)

    self.grams_ = grams

  def __eq__(self, a):
    return (self.grams_[0] == a.grams_[0] and
            self.grams_[1] == a.grams_[1])

  def __ne__(self, a):
    return not (self == a)

  def __hash__(self):
    return hash((self.grams_[0], self.grams_[1]))

  def __str__(self):
    return '[%s%s]' % (self.grams_[0], self.grams_[1])

  def __repr__(self):
    return self.__str__()


class Bigrams(object):
  @classmethod
  def FromString(cls, string):
    grams = Grams.FromString(string)

    bigrams = []
    prev = None
    for gram in grams:
      if prev is None:
        prev = gram
        continue

      bigram = Bigram([prev, gram])
      bigrams.append(bigram)
      prev = gram

    return bigrams


class BigramDict(object):
  """A dict-like object where key is a bigram and value is the # of occurrence"""
  @classmethod
  def FromBigrams(cls, bigrams):
    """From list of Bigram

    Args:
      bigrams: list of Bigram
    """
    self = cls()

    for bigram in bigrams:
      occurrence = self.dict_.get(bigram, 0)
      self.dict_[bigram] = occurrence + 1

    return self

  @classmethod
  def FromString(cls, string):
    return cls.FromBigrams(Bigrams.FromString(string))

  @classmethod
  def FromStringList(cls, str_list):
    new_obj = cls()
    for string in str_list:
      new_one = cls.FromBigrams(Bigrams.FromString(string))
      new_obj = new_obj + new_one
    return new_obj

  def __init__(self):
    self.dict_ = {}

  def __getitem__(self, key):
    return self.dict_[key]

  def __setitem__(self, key, value):
    self.dict_[key] = value

  def __iter__(self):
    for k, v in self.dict_.iteritems():
      yield k

  def iteritems(self):
    for k, v in self.dict_.iteritems():
      yield k, v

  def get(self, key, default=None):
    return self.dict_.get(key, default)

  def __add__(self, a):
    new_obj = BigramDict()
    for k, v in self.iteritems():
      org_v = new_obj.get(k, 0)
      new_obj.dict_[k] = org_v + 1

    for k, v in a.iteritems():
      org_v = new_obj.get(k, 0)
      new_obj.dict_[k] = org_v + 1

    return new_obj

  def __str__(self):
    return ','.join(['%s: %s' % (k, v) for k, v in self.iteritems()])

  def __repr__(self):
    return self.__str__()

  def __eq__(self, a):
    return cmp(self.dict_, a.dict_) == 0

  def __ne__(self, a):
    return not (self == a)


class Document(object):
  def __init__(self, void_p, bigram_dict):
    """Constructor

    Args:
      void_p: points to the original object provide this index.
      bigram_dict: BigramDict
    """
    self.void_p_ = void_p
    self.bigram_dict_ = bigram_dict
    self.score_ = 0

  def Clone(self):
    """Return a clean copy of this object"""
    if self.score_:
      raise ValueError('This copy is not clean. Cannot be cloned.')

    return copy.copy(self)

  @property
  def void_p(self):
    return self.void_p_

  @property
  def score(self):
    return self.score_

  def Match(self, keyword):
    """Count the match numner in this document.

    Args:
      keyword: BigramDict

    Return:
      int: number of match (Score)
    """
    num_match = 0
    for bigram in keyword:
      num_match += self.bigram_dict_.get(bigram, 0)

    self.score_ = num_match
    return num_match


class Documents(object):
  """Collection of Document"""
  def __init__(self, documents):
    """Constructor

    Args:
      documents: list of Document
    """
    self.documents_ = documents

  def Search(self, keyword):
    """Search with a keyword.

    Args:
      keyword: BigramDict

    Returns:
      sorted list of Document.
    """
    # Get a clean copy for all
    docs = [doc.Clone() for doc in self.documents_]

    for doc in docs:
      doc.Match(keyword)

    docs = sorted(docs, cmp=lambda x, y: -cmp(x.score, y.score))

    return docs
