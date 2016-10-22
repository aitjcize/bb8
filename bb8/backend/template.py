# -*- coding: utf-8 -*-
"""
    A Small and Fast Template Engine
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implementes a small and fast template engine for bb8.
    Althrough there are already a lot of templating engine out there (Moka,
    Jinja2, etc.), they are usually too slow and provide a lot more features
    that we don't need. Thus we implement our own small template engine so we
    can not only render fast and light weight, but also allow our own custom
    syntax.

    Currently, here are the template syntax we want to support.

    1. Attribute/Key access:
       Given a dictionary;
       {'key1': {'key2': {'key3': 'Test'}}}

       We should able to render it with:
       {{key1.key2.key3}}

       Grammar: expr := keypath1.keypath2....

       If a value indicated by the keypath is a list/tuple, a user can index
       it with the following synax:

       Given a dictionary:
       {'key1': {'key2': [0, 1, 2, 3]}}

       {{key1.key2#2}}
       will give as '2'

    2. Multiple Key (one-of key-path support):
       A user may render the template with:
       {{key1.key2,key3,key4}}

       If 'key1' does not exist, 'key3' will be used. If 'key3' does not
       exist, 'key4' will be used. So on and so forth.

    3. Filter:
       A user may pipe the result into a filter function:
       {{key1.key2|upper}}

    4. Conditional:
       {{key1.key2|upper if condition else key3.key4}}


    Grammar:

    key : ID

    value : value '.' key
          | key '#' NUMBER
          | key

    values : values ',' value
           | value

    function_arg : string_literal
                 | integer

    function_args : function_args ',' function_arg
                  | function_arg

    filter : filter_name '(' function_args ')'
           | filter_name

    condition_expr : value
                   | value OP value

    exprs : values
          | values '|' filter
          | values 'if' condition_expr 'else' values


    Copyright 2016 bb8 Authors
"""

import collections
import logging
import re

import enum

# Use relative import here so we can used it in app_api
from template_filters import FILTERS


HAS_VARIABLE_RE = re.compile('{{(.*?)}}')


class Token(enum.Enum):
    WHITESPACE = 'WHITESPACE'
    STRING_LITERAL = 'STRING_LITERAL'
    COMMA = 'COMMA'
    DOT = 'DOT'
    SHARP = 'SHARP'
    EQUALS = 'EQUALS'
    LT = 'LT'
    GT = 'GT'
    LE = 'LE'
    GE = 'GE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    PIPE = 'PIPE'
    TRUE = 'True'
    FALSE = 'False'
    ID = 'ID'
    IF = 'IF'
    ELSE = 'ELSE'
    NUMBER = 'NUMBER'

CONDITIONAL_TOKENS = [Token.EQUALS, Token.LT, Token.LE, Token.GT, Token.GE]
VALUE_TOKENS = [Token.STRING_LITERAL, Token.NUMBER, Token.TRUE, Token.FALSE]
VALUE_STARTING_TOKENS = VALUE_TOKENS + [Token.ID]

TokenResult = collections.namedtuple('TokenResult', ['type', 'value'])


token_rules = [
    (Token.WHITESPACE, re.compile(r'\s+'), None),
    (Token.STRING_LITERAL, re.compile(r"'[^']*'"), lambda x: x[1:-1]),
    (Token.COMMA, re.compile(r','), None),
    (Token.DOT, re.compile(r'\.'), None),
    (Token.SHARP, re.compile(r'#'), None),
    (Token.EQUALS, re.compile(r'=='), None),
    (Token.LT, re.compile(r'<'), None),
    (Token.GT, re.compile(r'>'), None),
    (Token.LE, re.compile(r'<='), None),
    (Token.GE, re.compile(r'>='), None),
    (Token.LPAREN, re.compile(r'\('), None),
    (Token.RPAREN, re.compile(r'\)'), None),
    (Token.PIPE, re.compile(r'\|'), None),
    (Token.IF, re.compile(r'if'), None),
    (Token.ELSE, re.compile(r'else'), None),
    (Token.NUMBER, re.compile(r'-?[0-9]+'), int),
    (Token.TRUE, re.compile(r'True'), lambda unused_x: True),
    (Token.FALSE, re.compile(r'False'), lambda unused_x: False),
    (Token.ID, re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'), None),
]


def to_unicode(text):
    if text is None:
        return None

    if not isinstance(text, unicode):
        return unicode(text, 'utf8')
    return text


def tokenize(template):
    """Tokenize the template into tokens.

    A brute force tokenizer that match regular expression against current
    buffer.
    """
    result = []
    while template:
        for token, rule, convert in token_rules:
            m = rule.match(template)
            if m:
                text = m.group(0)
                value = m.group(0)
                if token != Token.WHITESPACE:
                    if convert:
                        value = convert(value)
                    result.append(TokenResult(token, value))
                template = template[len(text):]
                break
    return result


class ParserError(Exception):
    pass


def peek(tokens):
    if len(tokens) <= 1:
        return None
    return tokens[1]


class ParserContext(object):
    def __init__(self, variables, filters=None):
        filters = filters or {}
        self.filters = dict(FILTERS, **filters)
        self.variables = variables
        self.value = None
        self.func_name = None
        self.args = []


def parse_function_args(context, tokens, evaluate=True):
    args = []
    context.args = []
    while tokens:
        token = tokens[0]
        if token.type == Token.NUMBER:
            args.append(token.value)
        elif token.type == Token.STRING_LITERAL:
            args.append(token.value)
        elif token.type == Token.COMMA:
            pass
        elif token.type == Token.RPAREN:
            if evaluate:
                context.args = args
            return tokens[1:]
        else:
            raise ParserError('Invalid token `(%s, %s)\' when parsing '
                              'function argument' % tokens[0])
        tokens = tokens[1:]


def parse_index(context, tokens, evaluate=True):
    token = tokens[0]
    if token.type == Token.NUMBER:
        if evaluate:
            try:
                context.value = context.value[token.value]
            except IndexError, e:
                raise ParserError('Invalid index `%s\': %s' % (token.value, e))
    else:
        raise ParserError('Invalid token `(%s, %s)\', expecting NUMBER' %
                          token)
    return tokens[1:]


def parse_filter(context, tokens, evaluate=True):
    def call_filter():
        if not evaluate:
            return

        filtr = context.filters.get(context.func_name)
        if filtr is None:
            raise ParserError('Filter `%s\' not found' % token.value)
        try:
            if context.args:
                filtr = filtr(*context.args)
            context.value = filtr(context.value)
        except Exception as e:
            logging.exception(e)
            raise ParserError('Function `%s` execution error: %s' %
                              (context.func_name, e))

    context.args = []
    while tokens:
        token = tokens[0]
        if token.type == Token.ID:
            context.func_name = token.value
            next_token = peek(tokens)
            if not next_token or next_token.type != Token.LPAREN:
                call_filter()
                return tokens
        elif token.type == Token.LPAREN:
            tokens = parse_function_args(context, tokens[1:], evaluate)
            call_filter()
            return tokens
        else:
            return tokens

        tokens = tokens[1:]


def parse_value(context, tokens, evaluate=True):
    context.value = None

    prev_token = None
    while tokens:  # pylint: disable=R0101
        token = tokens[0]
        if token.type in VALUE_TOKENS:
            if evaluate:
                context.value = token.value
            return tokens[1:]
        elif token.type == Token.ID:
            if evaluate:
                key = tokens[0].value
                if context.value is None:
                    context.value = context.variables.get(key)
                    if context.value is None:
                        # Variable does not exist, set evaluate to False
                        evaluate = False
                else:
                    if hasattr(context.value, key):
                        context.value = getattr(context.value, key)
                    else:
                        try:
                            context.value = context.value[key]
                        except (TypeError, KeyError):
                            # Invalid attribute, result the result
                            context.value = None
                            evaluate = False
        elif token.type == Token.LPAREN:
            tokens = parse_function_args(context, tokens[1:], evaluate)
            try:
                context.value = context.value(*context.args)
                continue
            except Exception as e:
                raise ParserError('Function `%s` execution error: %s' %
                                  (prev_token.value, e))
        elif token.type == Token.SHARP:
            tokens = parse_index(context, tokens[1:], evaluate)
        elif token.type == Token.DOT:
            pass
        else:
            return tokens

        prev_token = token
        tokens = tokens[1:]

    return tokens


def parse_values(context, tokens, evaluate=True):
    context.value = None

    result = None
    while tokens:
        token = tokens[0]
        if token.type in VALUE_STARTING_TOKENS:
            tokens = parse_value(context, tokens, evaluate)
            if context.value and evaluate:
                result = context.value
                evaluate = False
            continue
        elif token.type == Token.COMMA:
            pass
        else:
            context.value = result
            return tokens

        tokens = tokens[1:]

    return tokens


def parse_if_else(context, tokens):
    true_value = context.value

    tokens = parse_value(context, tokens)
    left_value = context.value

    if not tokens:
        raise ParserError('syntax error: unexpected end of input when parsing '
                          'if else expression')

    token = tokens[0]
    if token.type == Token.ELSE:
        if bool(left_value):
            tokens = parse_values(context, tokens[1:], evaluate=False)
            context.value = true_value
            return tokens

        return parse_value(context, tokens[1:])
    elif token.type in CONDITIONAL_TOKENS:
        op = token.type
        tokens = parse_value(context, tokens[1:])
        right_value = context.value
        result = False
        if op == Token.EQUALS:
            result = left_value == right_value
        elif op == Token.LT:
            result = left_value < right_value
        elif op == Token.LE:
            result = left_value <= right_value
        elif op == Token.GT:
            result = left_value > right_value
        elif op == Token.GE:
            result = left_value >= right_value

        if result:  # The result evaluates to True, return true_value
            tokens = parse_values(context, tokens[1:], evaluate=False)
            context.value = true_value
            return tokens

        if tokens[0].type != Token.ELSE:
            raise ParserError('syntax error: expecting ELSE, got %s',
                              tokens[0].type)

        return parse_values(context, tokens[1:])
    else:
        raise ParserError('syntax error: expecting boolean expression, '
                          'got %s' % token)


def parse_exprs(context, tokens):
    while tokens:
        token = tokens[0]
        if token.type in VALUE_STARTING_TOKENS:
            tokens = parse_values(context, tokens)
            continue
        elif token.type == Token.PIPE:
            tokens = parse_filter(context, tokens[1:])
        elif token.type == Token.IF:
            tokens = parse_if_else(context, tokens[1:])
            continue

        tokens = tokens[1:]


def parse_root(context, tokens):
    if tokens[0].type in VALUE_STARTING_TOKENS:
        parse_exprs(context, tokens)


def parse(template, variables):
    context = ParserContext(variables)
    tokens = tokenize(template)
    parse_root(context, tokens)

    if not context.value:
        return None
    elif isinstance(context.value, str):
        return unicode(context.value, 'utf8')
    elif isinstance(context.value, unicode):
        return context.value
    else:
        return unicode(str(context.value), 'utf8')


def Render(template, variables):
    """Render template with variables."""
    if template is None:
        return None

    def replace(m):
        ret = None
        try:
            ret = parse(m.group(1), variables)
        except Exception as e:
            logging.exception(e)
        return ret if ret else m.group(0)
    return HAS_VARIABLE_RE.sub(replace, to_unicode(template))
