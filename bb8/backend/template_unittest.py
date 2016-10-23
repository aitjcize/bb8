#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for bb8 Template Engine
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.template import Render


class TemplateUnittest(unittest.TestCase):
    def test_variable_indexing(self):
        variables = {'a': {'b': {'c': 3}}}
        self.assertEquals(Render('{{a.b.c}}', variables), '3')

        variables = {}
        self.assertEquals(Render('{{a.b.c}}', variables), '{{a.b.c}}')

        variables = {'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{a.b.c,k.j|upper}}', variables), 'AAA')

        variables = {'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{k.j,a.b|upper}}', variables), 'AAA')

        variables = {'a': 1, 'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{a.b,k.j|upper}}', variables), 'AAA')

        variables = {'a': 1, 'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{h,j,k.j|upper}}', variables), 'AAA')

    def test_variable_function_call(self):
        variables = {'a': {'b': {'c': lambda x: {'d': x}}}}
        self.assertEquals(Render('{{a.b.c(4).d}}', variables), '4')

    def test_variable_result_indexing(self):
        variables = {'a': [1, 2, 3, 4, 5]}
        self.assertEquals(Render('{{a#0}}', variables), '1')

        variables = {'a': {'b': {'c': lambda x: {'d': [1, 2, 3]}}}}
        self.assertEquals(Render('{{a.b.c(4).d#1}}', variables), '2')
        self.assertEquals(Render('{{a.b.c(4).d#-1}}', variables), '3')

    def test_filter(self):
        variables = {'a': 'test_value'}
        self.assertEquals(Render('{{a|upper}}', variables), 'TEST_VALUE')

        variables = {'a': {'b': 'test_value'}}
        self.assertEquals(Render('{{a.b|truncat(4)}}', variables), 'test')

    def test_if_else(self):
        variables = {
            'a': {'b': 'test_value', 'c': 'test_value2'},
            'settings': {'subscribe': True}
        }
        self.assertEquals(Render("{{a.c if a.b == 'test_value' else 'A'}}",
                                 variables), 'test_value2')
        self.assertEquals(Render("{{a.c if a.b.startswith('test') else 'A'}}",
                                 variables), 'test_value2')
        self.assertEquals(Render("{{a.c if a.b == 'asdf' else 'A'}}",
                                 variables), 'A')
        self.assertEquals(Render("{{'Yes' if settings.subscribe else 'No'}}",
                                 variables), 'Yes')
        self.assertEquals(Render("{{'Yes' if settings.subscribe == True "
                                 "else 'No'}}", variables), 'Yes')


if __name__ == '__main__':
    unittest.main()
