#!/usr/bin/python
# -*- coding: utf-8 -*-
"""For the food association table.

  Foods -- the collections of all foods

    Food: kind: DISH
      |    |-- FoodName:
      |         |-- '臭豆腐', 'zh_TW'
      |
      |
      |
    Food ----------------------- Food ------------------------ Food
     |-- kind: ELEM               |-- kind: DISH                |-- kind: DISH
     |                            |                             |
     |-- FoodNmae                 |-- FoodName                  |-- FoodName
     |    |-- '豆腐', 'zh_TW'          |-- '豆腐鍋', 'zh_TW'         |-- '火鍋'
     |
     |-- FoodNmae
     |    |-- 'tofu', 'en'
     |
     |-- FoodName
          |-- '豆腐', 'ja'
"""

import argparse
import logging
import pickle
import pprint

import utils

pp = pprint.PrettyPrinter(indent=2)


class FoodName(object):
  """A text and its lang.

  In order to work with __str__ (for assertEqual) and __repr__ (for pformat),
  all names are saved in utf-8.
  """
  def __init__(self, name, lang):
    self.name_ = utils.Unicode(name).encode('utf-8')
    self.lang_ = utils.canonize_locale(utils.Unicode(lang).encode('utf-8'))

  def __str__(self):
    return '%s(%s)' % (self.name, self.lang)

  def __repr__(self):
    return self.__str__()  # for pformat

  def __hash__(self):
    return hash((self.name, self.lang))

  def __eq__(self, other):
    return (self.name, self.lang) == (other.name, other.lang)

  def __ne__(self, other):
    return not(self == other)

  @property
  def name(self):
    return self.name_

  @property
  def lang(self):
    return self.lang_


class Link(object):
  """A uni-direction link from food A to food B"""
  def __init__(self, origin, other):
    """Constructor

    Args:
      origin: Food. The origin food. Not really used. Just for debug.
      other: Food. The food where origin points to. For debug only.
    """
    self.origin_ = origin
    self.other_ = other
    self.scores_ = []  # array of float [0, 1].

  def __str__(self):
    return '==({0})=>{1}'.format(self.score, self.other.food_names[0])

  def __repr__(self):
    return self.__str__()

  @property
  def origin(self):
    return self.origin_

  @property
  def other(self):
    return self.other_

  @property
  def score(self):
    return sum(self.scores_) / len(self.scores_)

  def AddScore(self, score):
    self.scores_.append(score)


class Links(object):
  def __init__(self):
    self.links_ = {}  # key: the other food, value: Link

  def __str__(self):
    return ', '.join(['{}'.format(x) for x in self.links_.values()])

  def __repr__(self):
    return self.__str__()

  def __iter__(self):
    return self.links_.iteritems()

  def Get(self, dst_food, src_food=None):
    """Returns a link object no matter if dst_food is existing or not.

    If the dst_food is not existing, a new Link object is created and returned.

    Args:
      dst_food: Food.
      src_food: Food. For creation only.

    Returns:
      Link
    """
    link = self.links_.get(dst_food)
    if not link:
      if not src_food:
        raise ValueError(
            'src_food must be given if dst_food(%s) is not existing' % dst_food)

      link = Link(src_food, dst_food)
      self.links_[dst_food] = link

    return link

  def get(self, dst_food):
    """Query if contains a link with 'dst_food'.

    Args:
      dst_food: Food. Used to match the other part of link.

    Returns:
      None: No link.
      Link: The link with dst_food.
    """
    return self.links_.get(dst_food)

  def Scores(self):
    """Returns all scores (and its dst_food). Scores are normalized.

    Returns:
      array of (dst_food, score)
    """
    links = self.links_.values()
    total_score = sum([l.score for l in links])
    return [(l.other, l.score / total_score) for l in links]


class Food(object):
  """Food"""
  def __init__(self, food_names, kind=None):
    """Constructor

    Args:
      food_names: list of FoodName. The food name and its alias.
      kind: The food kind.
    """
    self.kind_ = kind
    self.food_names_ = food_names
    self.links_ = Links()  # key: the other food, value: Link

  def __str__(self):
    food_names = ', '.join(['{}'.format(x) for x in self.food_names_])
    return '<{0}, {1}:: {2}>'.format(self.kind_, food_names, self.links_)

  def __repr__(self):
    return self.__str__()

  @classmethod
  def ImportSrc(cls, src, kind):
    """Import a Food from the source part of associate_data.data.

    Args:
      src: list of (name, lang)

    Returns:
      Food.
    """
    food_names = [FoodName(name, lang) for name, lang in src]
    return Food(food_names, kind)

  @classmethod
  def ImportDst(cls, dst):
    """Import a Food from the destination part of associate_data.data.

    Args:
      dst: list of (name, lang, score).

    Returns:
      list of (FoodName, score): Score is float.
    """
    return [(FoodName(name, lang), score) for name, lang, score in dst]

  @property
  def kind(self):
    return self.kind_

  @property
  def food_names(self):
    return self.food_names_

  @property
  def links(self):
    return self.links_

  def AddDstFood(self, dst_food, score):
    """Add a destination food into the outgoing link.

    Args:
      dst_food: Food.
      score: float [0, 1]
    """
    link = self.links_.Get(dst_food, self)
    link.AddScore(score)

  def GetLangName(self, lang):
    """Get the food name in 'lang'.

    Args:
      lang: str. The locale/langugae name. Must be canonized.

    Returns:
      None: This food doesn't has a name in this language.
      FoodName: The name for that language.
    """
    for food_name in self.food_names_:
      if food_name.lang == lang:
        return food_name

    return None


class Foods(object):
  """Collection of food"""
  def __init__(self):
    self.foods_ = []
    self.food_by_name_ = {}  # key, value: food_name --> Food

  @classmethod
  def ImportFromData(cls, data):
    foods = Foods()

    unresolved = []  # array of tuple (src_food, dst_food_name, score)
    for kind, src, dst in data:
      src_food = Food.ImportSrc(src, kind)

      # Merge into the food if any of its name is existing.
      for food_name in src_food.food_names:
        existing_food = foods.food_by_name_.get(food_name)
        if existing_food:
          # TODO: merge 2 src foods.
          print 'Merging two src foods: {0} and {1}'.format(
                  src_food, existing_food)
          raise NotImplementedError
          if merged_once:
            raise NotImplementedError  # TODO: this one links the existing ones.
        else:
          foods.food_by_name_[food_name] = src_food
      foods.foods_.append(src_food)

      # Resolve (or create unresolved) dst foods.
      dst_foods_and_scores = Food.ImportDst(dst)
      for dst_food_name, score in dst_foods_and_scores:
        existing_food = foods.food_by_name_.get(dst_food_name)
        if existing_food:
          src_food.AddDstFood(existing_food, score)
        else:
          unresolved.append((src_food, dst_food_name, score))

    # 2nd phase. Resolve again.
    for src_food, dst_food_name, score in unresolved:
      existing_food = foods.food_by_name_.get(dst_food_name)
      if existing_food:
        src_food.AddDstFood(existing_food, score)
      else:
        # Create a new Food for dst_food
        new_food = Food([dst_food_name])
        src_food.AddDstFood(new_food, score)
        foods.food_by_name_[dst_food_name] = new_food
        foods.foods_.append(new_food)

    # create reversed links
    for src_food in foods.food_by_name_.values():
      for _, link in src_food.links:
        if not link.other.links.get(link.origin):
          link.other.AddDstFood(link.origin, link.score)

    return foods

  @classmethod
  def ImportFromPickle(self, filename):
    return pickle.load(open(filename, 'rb'))

  def ExportToPickle(self, filename):
    pickle.dump(self, open(filename, 'wb'), pickle.HIGHEST_PROTOCOL)

  def GetByKind(self, kind, inverse=False):
    """Returns all foods of the kind.

    Args:
      kind: None, DISH, or ELEM
      inverse: True to return NOT cases.

    Returns:
      array of Food.
    """
    return [x for x in self.foods_ if (x.kind_ == kind) != inverse]

  def GetAllNoKind(self):
    return self.GetByKind(None)

  def GetAllElements(self):
    return self.GetByKind(associate_data.ELEM)

  def GetNonElems(self):
    return self.GetByKind(associate_data.ELEM, inverse=True)

  def GetAllDishes(self):
    return self.GetByKind(associate_data.DISH)

  def ZeroScores(self):
    """Empty score dict for want.py

    Returns:
      dict with:
        key: (dst food name (utf-8), dst food lang (utf-8))
        value: 0.0
    """
    return {(food_name.name, food_name.lang): 0.0
        for food_name in self.food_by_name_.keys()}

  def GetLikes(self, src_name, src_lang):
    """Get the likes of a food (by its name).

    Args:
      src_name: utf-8 str.
      src_lang: utf-8 str.

    Returns:
      list of (dst food name (utf-8), dst food lang (utf-8), score).
    """
    src_food = self.food_by_name_.get(FoodName(src_name, src_lang))
    return [(food_name.name, food_name.lang, score)
        for dst_food, score in src_food.links.Scores()
        for food_name in dst_food.food_names]


def Main():
  parser = argparse.ArgumentParser(description='Process some integers.')
  parser.add_argument('action', choices=['gen-pickle', 'show-no-kind'])
  parser.add_argument('--pickle', default=config.FOOD_PICKLE_FILENAME)
  args = parser.parse_args()

  foods = Foods.ImportFromData(associate_data.data)

  if args.action == 'gen-pickle':
    print 'Saving to %s ...' % args.pickle
    foods.ExportToPickle(args.pickle)

  elif args.action == 'show-no-kind':
    no_kind = foods.GetAllNoKind()

    for food in no_kind:
      print """  (None, [(u"%s", u"%s"),],
                                      []),
""" % (food.food_names[0].name, food.food_names[0].lang)

  else:
    raise ValueError('Unknown action: %s' % action)

if __name__ == '__main__':
  Main()
