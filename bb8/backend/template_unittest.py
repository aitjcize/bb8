#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for bb8 Template Engine
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.template import Render, ParserError


class TemplateUnittest(unittest.TestCase):
    def test_arithmetic_operations(self):
        variables = {'a': 1, 's': 'A'}

        # Basic plus and minus
        self.assertEquals(Render('{{a + 1}}', variables), '2')
        self.assertEquals(Render('{{a + 1 + 3}}', variables), '5')
        self.assertEquals(Render('{{a - 1}}', variables), '0')

        # String
        self.assertEquals(Render("{{s + ' dog'}}", variables), 'A dog')

        # Conditional
        self.assertEquals(Render("{{a > 0}}", variables), 'True')
        self.assertEquals(Render("{{2 > 1}}", variables), 'True')
        self.assertEquals(Render("{{2 >= 1}}", variables), 'True')
        self.assertEquals(Render("{{2 < 1}}", variables), 'False')
        self.assertEquals(Render("{{2 <= 1}}", variables), 'False')

        self.assertEquals(Render("{{not 1}}", variables), 'False')
        self.assertEquals(Render("{{not False}}", variables), 'True')

    def test_variable_indexing(self):
        variables = {'a': {'b': {'c': 3}}}
        self.assertEquals(Render('{{a.b.c}}', variables), '3')

        variables = {}
        self.assertEquals(Render('{{a.b.c}}', variables), '')

        variables = {'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{a.b.c;k.j|upper}}', variables), 'AAA')

        variables = {'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{k.j;a.b|upper}}', variables), 'AAA')

        variables = {'a': 1, 'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{a.b;k.j|upper}}', variables), 'AAA')

        variables = {'a': 1, 'k': {'j': 'aaa'}}
        self.assertEquals(Render('{{h;j;k.j|upper}}', variables), 'AAA')

        variables = {'a': 1, 'k': {'j': [{'h': 2}, 3]}}
        self.assertEquals(Render("{{k.j#0.h}}", variables), '2')

    def test_variable_function_call(self):
        variables = {'a': {'b': {'c': lambda x: {'d': x}}}}
        self.assertEquals(Render('{{a.b.c(4).d}}', variables), '4')

        variables = {'a': {'b': {'c': lambda x, y: {'d': x + str(y)}}}}
        self.assertEquals(Render("{{a.b.c('4', 5).d}}", variables), '45')

        variables = {'a': {'b': lambda: 5}}
        self.assertEquals(Render("{{a.b() + 5}}", variables), '10')

        def upper(x):
            return x.upper()

        variables = {'a': 'abc', 'upper': upper}
        self.assertEquals(Render("{{upper(a + '.' + 'xyz')}}", variables),
                          'ABC.XYZ')

        self.assertEquals(Render("{{upper(a|truncat(1))}}", variables), 'A')

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
        self.assertEquals(Render('{{a.b|truncat(4)|upper}}', variables),
                          'TEST')

        variables = {'target': 'Isaac', 'name': 'bb8', 'age': 100}
        text = Render('Hi {{target|upper}}, I am {{name}}. '
                      'I am {{age|inc|str}} years old.', variables)
        self.assertEquals(text, 'Hi ISAAC, I am bb8. I am 101 years old.')

    def test_if_else(self):
        variables = {
            'a': {'b': 'test_value', 'c': 'test_value2', 'd': True},
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
        self.assertEquals(Render("{{a.b + a.c if a.b + a.c == "
                                 "'test_valuetest_value2' else 'A'}}",
                                 variables), 'test_valuetest_value2')

        # Test value_expr
        self.assertEquals(Render("{{a.c|upper if a.d else 'a'|upper}}",
                                 variables), 'TEST_VALUE2')

        self.assertEquals(Render("{{a.c|upper if not a.d else 'a'|upper}}",
                                 variables), 'A')

        self.assertEquals(Render("{{a.c|upper if 1 + 1 else 'a'|upper}}",
                                 variables), 'TEST_VALUE2')

        self.assertEquals(Render("{{a.c|upper if 1 - 1 else 'a'|upper}}",
                                 variables), 'A')

        self.assertEquals(Render("{{a.c|upper if 1 + 1 + 2 else 'a'|upper}}",
                                 variables), 'TEST_VALUE2')

    def test_invalid_syntax(self):
        variables = {'a': {'b': 1}, 'c': [1, 2, 3]}

        self.assertEquals(Render(None, variables), None)

        with self.assertRaises(ParserError):
            Render("{{a * 1}}", variables)

        with self.assertRaises(ParserError):
            Render("{{a not a}}", variables)

        with self.assertRaises(ParserError):
            Render("{{a.c#1a.b}}", variables)

        with self.assertRaises(ParserError):
            Render("{{else}}", variables)

        with self.assertRaises(ParserError):
            Render("{{a.b if a.b if}}", variables)

        with self.assertRaises(ParserError):
            Render("{{a.b if}}", variables)

        with self.assertRaises(ParserError):
            Render('{{a.b if a.b else}}', variables)

        with self.assertRaises(ParserError):
            Render('{{a.b if a.b else if}}', variables)

        with self.assertRaises(ParserError):
            Render('{{a.b|some_filter}}', variables)

        with self.assertRaises(ParserError):
            Render('{{a.b(1)}}',
                   {'a': {'b': lambda x: x.none_exist}})


if __name__ == '__main__':
    unittest.main()
