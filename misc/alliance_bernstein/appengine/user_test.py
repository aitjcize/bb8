#!/usr/bin/env python
import unittest

import food
import user

class DbUpdateMock(object):
  """Mock up for db update"""
  def __init__(self):
    self.Init()

  def __call__(self, serialized_data):
    self.fired_ += 1
    self.fired_data_ = serialized_data

  def Init(self):
    self.fired_ = 0  # num of fired count
    self.fired_data_ = None

  @property
  def fired(self):
    return self.fired_

  @property
  def fired_data(self):
    return self.fired_data_


class TestDietHabit(unittest.TestCase):
  def setUp(self):
    def DbUpdate(serialized_data):
      print 'FIXME: serialized_data=%r' % serialized_data

    self.db_update_mock_ = DbUpdateMock()
    self.diet_habit_ = user.DietHabit(self.db_update_mock_)

  def test_normal(self):
    # Not exist yet
    food1 = food.FoodName('Food 1', 'zh_TW')
    self.assertEqual(self.diet_habit_.Get(food1), user.DietHabit.DEFAULT_VALUE)
    self.assertEqual(self.diet_habit_.GetScore(food1), 1.0)

    # Add it (+) : 5 --> 8
    self.diet_habit_.Update([(True, food1)])
    self.assertEqual(self.db_update_mock_.fired, 1)
    self.assertAlmostEqual(self.diet_habit_.GetScore(food1), 1.33333333)
    self.diet_habit_.Update([(True, food1)])
    self.assertEqual(self.db_update_mock_.fired, 2)
    self.diet_habit_.Update([(True, food1)])
    self.assertEqual(self.db_update_mock_.fired, 3)
    self.diet_habit_.Update([(True, food1)])
    self.assertEqual(self.db_update_mock_.fired, 3)
    self.assertEqual(self.diet_habit_.GetScore(food1), 2.0)

    # Another food (-) : 5 --> 2
    food2 = food.FoodName('Food 2', 'zh_TW')
    self.db_update_mock_.Init()
    self.diet_habit_.Update([(False, food2)])
    self.assertEqual(self.db_update_mock_.fired, 1)
    self.assertAlmostEqual(self.diet_habit_.GetScore(food2), 0.83333333)
    self.diet_habit_.Update([(False, food2)])
    self.assertEqual(self.db_update_mock_.fired, 2)
    self.diet_habit_.Update([(False, food2)])
    self.assertEqual(self.db_update_mock_.fired, 3)
    self.diet_habit_.Update([(False, food2)])
    self.assertEqual(self.db_update_mock_.fired, 3)
    self.assertEqual(self.diet_habit_.GetScore(food2), 0.5)


if __name__ == '__main__':
  unittest.main()
