"""This is used to save the user's profile or preference."""

import cPickle as pickle
import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb


def PossibilityWeight(count, max_count, mid_count, min_count):
  #  count == max: 2.0
  #           mid: 1.0
  #           min: 0.5
  if count > mid_count:
    return 1.0 + 1.0 / (max_count - mid_count) * (count - mid_count)
  else:
    return 1.0 - 0.5 / (mid_count - min_count) * (mid_count - count)

class DietHabit(object):
  FIELD_NAME='DietHabit'
  MIN_VALUE=2
  MAX_VALUE=8
  DEFAULT_VALUE=5

  def __init__(self, db_update):
    """Constructor

    Args:
      db_update: a callable object to update the database entry, which
                 accepts a string (serialized data).
    """
    self.db_update_ = db_update

    # key=food.FoodName, value=int:[2-8]
    self.records_ = {}

  @classmethod
  def Import(cls, data):
    return pickle.loads(data)

  def Export(self):
    return pickle.dumps(self, pickle.HIGHEST_PROTOCOL)

  def Get(self, food_name):
    """Gets the count value.

    Args:
      food_name: food.FoodName

    Returns:
      integer: count.
    """
    rec = self.records_.get(food_name)
    if rec is None:
      return self.DEFAULT_VALUE
    else:
      return min(max(rec, self.MIN_VALUE), self.MAX_VALUE)

  def GetScore(self, food_name):
    """Gets the score for possibility.

    Args:
      food_name: food.FoodName

    Returns:
      [0.0, 1.0]
    """
    count = self.Get(food_name)
    return PossibilityWeight(
        count, self.MAX_VALUE, self.DEFAULT_VALUE, self.MIN_VALUE)

  def Update(self, selected):
    """Update the count according to the user's selection.

    Args:
      selected: list of (plus, food.FoodName) where plus==True if user likes it.

    Returns:
      bool: True if the count is dirty and requires write-back to database.
    """
    logging.debug('FIXME: self.records_=%r', self.records_)
    dirty = False
    for plus, food_name in selected:
      count = self.Get(food_name)
      if plus and count < self.MAX_VALUE:
        self.records_[food_name] = count + 1
        dirty = True
      elif not plus and count > self.MIN_VALUE:
        self.records_[food_name] = count - 1
        dirty = True

    logging.debug('FIXME: Update.dirty=%d', dirty)
    if dirty:
      logging.debug('FIXME: self.records_=%r', self.records_)
      self.db_update_(self.Export())

    return dirty


class UserModel(ndb.Model):
  """The database model used to save user's parameters."""
  # id/key = '$uid.$field'
  value = ndb.BlobProperty()


class DbUpdate(object):
  """Update both DB and memcache"""
  def __init__(self, uid_field):
    self.uid_field_ = uid_field

  def __call__(self, serialized_data):
    """The callback function used when data is changed."""
    # Update dadatbase first
    key = ndb.Key(UserModel, self.uid_field_)
    user_entity = UserModel(key=key, value=serialized_data)
    user_entity.put()

    # Then memcache
    logging.debug('FIXME: user_entity.key: %r', user_entity.key)
    memcache.set(key=self.uid_field_, value=serialized_data)

def GetUserParameter(uid, cls):
  """Returns an instance.

  Args:
    uid: str: the user id
    cls: class: the class if new instance is needed to create.

  Returns:
    An cls instance.
  """
  uid_field = '.'.join([uid, cls.FIELD_NAME])
  cached_data = memcache.get(key=uid_field)
  if cached_data is not None:
    logging.debug('FIXME: @MEMCACHE cached_data: %r', cached_data)
    return pickle.loads(cached_data)

  # load from db
  db_key = ndb.Key(UserModel, uid_field)
  user_entity = db_key.get()
  if user_entity:
    data = user_entity.value
    logging.debug('FIXME: @DATABASE db_key: %r data: %r', db_key, pickle.loads(data).records_)
  else:
    logging.debug('FIXME: @NEW cached_data: %r', cached_data)
    data = cls(db_update=DbUpdate(uid_field)).Export()
    # Don't create entity in DB until the user really updates the value.

  # Stay in cache
  memcache.set(key=uid_field, value=data)

  return pickle.loads(data)
