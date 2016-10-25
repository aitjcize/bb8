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

    function_arg : string_literal
                 | number

    function_args : function_args ',' function_arg
                  | function_arg

    base_value : base_value '.' key
               | base_value '#' NUMBER
               | key '(' function_args ')
               | key

    value : pure_value
          | NOT pure_value

    values : values ',' value
           | value

    values_expr : values_expr op values_expr
                | values

    filtered_value_expr : filtered_value_expr '|' filter
                        | values_expr

    filter : filter_name '(' function_args ')'
           | filter_name

    exprs : filtered_value_expr
          | filtered_value_expr 'if' value 'else' filtered_value_expr


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
    NOT = 'NOT'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    ID = 'ID'
    IF = 'IF'
    ELSE = 'ELSE'
    NUMBER = 'NUMBER'

CONDITIONAL_TOKENS = [Token.EQUALS, Token.LT, Token.LE, Token.GT, Token.GE]
VALUE_TOKENS = [Token.STRING_LITERAL, Token.NUMBER, Token.TRUE, Token.FALSE,
                Token.NOT]
ARITHMETIC_TOKENS = [Token.PLUS, Token.MINUS]
VALUE_STARTING_TOKENS = VALUE_TOKENS + [Token.ID]

BINARY_OP = CONDITIONAL_TOKENS + ARITHMETIC_TOKENS

TokenResult = collections.namedtuple('TokenResult', ['type', 'value'])
Register = collections.namedtuple('Register', ['value', 'inverted'])


token_rules = [
    (Token.WHITESPACE, re.compile(r'\s+'), None),
    (Token.STRING_LITERAL, re.compile(r"'[^']*'"), lambda x: x[1:-1]),
    (Token.DOT, re.compile(r'\.'), None),
    (Token.COMMA, re.compile(r','), None),
    (Token.SHARP, re.compile(r'#'), None),
    (Token.EQUALS, re.compile(r'=='), None),
    (Token.LE, re.compile(r'<='), None),
    (Token.GE, re.compile(r'>='), None),
    (Token.LT, re.compile(r'<'), None),
    (Token.GT, re.compile(r'>'), None),
    (Token.LPAREN, re.compile(r'\('), None),
    (Token.RPAREN, re.compile(r'\)'), None),
    (Token.PIPE, re.compile(r'\|'), None),
    (Token.NUMBER, re.compile(r'-?[0-9]+'), int),
    (Token.PLUS, re.compile(r'\+'), None),
    (Token.MINUS, re.compile(r'-'), None),
    (Token.IF, re.compile(r'if'), None),
    (Token.ELSE, re.compile(r'else'), None),
    (Token.NOT, re.compile(r'not'), None),
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


class ParserError(Exception):
    pass


class VMError(Exception):
    pass


def tokenize(template):
    """Tokenize the template into tokens.

    A brute force tokenizer that match regular expression against current
    buffer.
    """
    result = []
    index = 0
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
                index += len(text)
                template = template[len(text):]
                break
        else:
            raise ParserError('Invalid token found at position %d' % index)
    return result


def peek(tokens):
    if len(tokens) <= 1:
        return None
    return tokens[1]


class ParserContext(object):
    def __init__(self, variables, filters=None):
        filters = filters or {}
        self.filters = dict(FILTERS, **filters)
        self.variables = variables
        self.evaluate = True
        self.value = None
        self.inverted = False
        self.func_name = None
        self.args = []
        self.stack = []

    def reset(self):
        self.value = None
        self.inverted = False
        self.args = []
        self.evaluate = True

    def push_op(self, token):
        """Push operation into the stack."""
        self.stack.append(token)

    def push(self):
        """Push current value into the stack."""
        self.stack.append(Register(self.value, self.inverted))
        self.value = None
        self.inverted = False

    def pop(self):
        """Pop value from stack."""
        self.value, self.inverted = self.stack.pop()

    def eval_bool(self):
        return bool(self.value) and not self.inverted

    def eval_attr(self, token):
        if token.type != Token.ID:
            raise ParserError('SyntaxError: expecting ID, got %s' % str(token))

        if self.evaluate:
            key = token.value
            if self.value is None:
                self.value = self.variables.get(key)
                if self.value is None:
                    # Variable does not exist, set evaluate to False
                    self.evaluate = False
            else:
                if hasattr(self.value, key):
                    self.value = getattr(self.value, key)
                else:
                    try:
                        self.value = self.value[key]
                    except (TypeError, KeyError):
                        # Invalid attribute, result the result
                        self.value = None
                        self.evaluate = False

    def eval_function(self):
        try:
            func = self.value
            self.value = self.value(*self.args)
        except Exception as e:
            raise ParserError('Function `%s` execution error: %s' % (func, e))

    def eval_filter(self):
        if not self.evaluate:
            return

        filtr = self.filters.get(self.func_name)
        if filtr is None:
            raise ParserError('Filter `%s\' not found' % self.func_name)
        try:
            if self.args:
                filtr = filtr(*self.args)
            self.value = filtr(self.value)
        except Exception as e:
            logging.exception(e)
            raise ParserError('Function `%s` execution error: %s' %
                              (self.func_name, e))

    def exec_op(self):
        op = self.stack.pop()
        if not isinstance(op, Token):
            raise VMError('can not execute, epxecting op, got %s' % str(op))

        arg2 = self.stack.pop()
        arg1 = self.stack.pop()

        arg1_val = arg1.value if not arg1.inverted else not arg1.value
        arg2_val = arg2.value if not arg2.inverted else not arg2.value

        try:
            if op == Token.EQUALS:
                result = arg1_val == arg2_val
            elif op == Token.LT:
                result = arg1_val < arg2_val
            elif op == Token.LE:
                result = arg1_val <= arg2_val
            elif op == Token.GT:
                result = arg1_val > arg2_val
            elif op == Token.GE:
                result = arg1_val >= arg2_val
            elif op == Token.PLUS:
                result = arg1_val + arg2_val
            elif op == Token.MINUS:
                result = arg1_val - arg2_val
        except Exception as e:
            raise VMError('Operation fail for %s: %e' % (op, e))

        self.value = result
        self.inverted = False

    def as_unicode_value(self):
        if self.inverted:
            self.value = not self.value

        if self.value is None:
            return None
        elif isinstance(self.value, str):
            return unicode(self.value, 'utf8')
        elif isinstance(self.value, unicode):
            return self.value
        else:
            return unicode(str(self.value), 'utf8')


def parse_function_args(context, tokens):
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
            if context.evaluate:
                context.args = args
            return tokens[1:]
        else:
            raise ParserError('Invalid token `(%s, %s)\' when parsing '
                              'function argument' % tokens[0])
        tokens = tokens[1:]


def parse_index(context, tokens):
    token = tokens[0]
    if token.type == Token.NUMBER:
        if context.evaluate:
            try:
                context.value = context.value[token.value]
            except Exception as e:
                raise ParserError('Invalid index `%s\': %s' % (token.value, e))
    else:
        raise ParserError('Invalid token %s, expecting NUMBER' % str(token))
    return tokens[1:]


def parse_filter(context, tokens):
    context.args = []

    if tokens[0].type != Token.ID:
        raise ParserError('Invalid token found %s, expecting ID' % tokens[0])

    context.func_name = tokens[0].value
    tokens = tokens[1:]
    if not tokens or (tokens and tokens[0].type != Token.LPAREN):
        context.eval_filter()
        return tokens

    if tokens[0].type == Token.LPAREN:
        tokens = parse_function_args(context, tokens[1:])
        context.eval_filter()
        return tokens

    return tokens


def parse_base_value(context, tokens):
    context.value = None

    value_parsed = False
    while tokens:
        token = tokens[0]
        if token.type in VALUE_TOKENS:
            if context.evaluate:
                context.value = token.value
            return tokens[1:]
        elif token.type == Token.ID:
            if value_parsed:
                raise ParserError('SyntaxError: expecting end of base_value '
                                  'expression, got %s' % str(token))
            context.eval_attr(token)
            tokens = tokens[1:]
            value_parsed = True
        elif token.type == Token.LPAREN:
            tokens = parse_function_args(context, tokens[1:])
            context.eval_function()
        elif token.type == Token.SHARP:
            tokens = parse_index(context, tokens[1:])
            value_parsed = True
        elif token.type == Token.DOT:
            context.eval_attr(tokens[1])
            tokens = tokens[2:]
            value_parsed = False
        else:
            return tokens

    return tokens


def parse_value(context, tokens):
    token = tokens[0]
    if token.type == Token.NOT:
        if context.evaluate:
            context.inverted = True
        tokens = tokens[1:]

    if token.type in VALUE_STARTING_TOKENS:
        return parse_base_value(context, tokens)

    raise ParserError('SyntaxError: expect BASE_VALUE or NOT, '
                      'got %s' % str(token))


def parse_values(context, tokens):
    context.reset()

    result = None
    new_value = True
    while tokens:
        token = tokens[0]
        if token.type in VALUE_STARTING_TOKENS:
            if not new_value:
                raise ParserError('SyntaxError: expecting COMMA, got %s' %
                                  str(token))
            tokens = parse_value(context, tokens)
            if context.value and context.evaluate:
                result = context.value
                context.evaluate = False
            if result is None:
                context.evaluate = True
            new_value = False
        elif token.type == Token.COMMA:
            tokens = tokens[1:]
            new_value = True
        else:
            context.value = result
            context.evaluate = True
            return tokens

    context.evaluate = True
    return tokens


def parse_values_expr(context, tokens):
    while tokens:
        token = tokens[0]
        if token.type in VALUE_STARTING_TOKENS:
            tokens = parse_values(context, tokens)
        elif token.type in BINARY_OP:
            op = token.type
            context.push()
            tokens = parse_values_expr(context, tokens[1:])
            context.push()
            context.push_op(op)
            context.exec_op()
        else:
            return tokens
    return tokens


def parse_filtered_value_expr(context, tokens):
    if not tokens:
        raise ParserError('SyntaxError: unexpected and if intput when parsing '
                          'filtered_value_expr')

    if tokens[0].type not in VALUE_STARTING_TOKENS:
        raise ParserError('SyntaxError: expecting value_expr, got %s' %
                          str(tokens[0]))

    tokens = parse_values_expr(context, tokens)

    while tokens:
        if tokens and tokens[0].type == Token.PIPE:
            tokens = parse_filter(context, tokens[1:])
        else:
            break

    return tokens


def parse_if_else(context, tokens):
    context.push()
    tokens = parse_values_expr(context, tokens)

    if not tokens:
        raise ParserError('SyntaxError: unexpected end of input when parsing '
                          'if else expression')
    token = tokens[0]
    if token.type == Token.ELSE:
        tokens = tokens[1:]
        if context.eval_bool():
            tokens = parse_filtered_value_expr(context, tokens)
            context.pop()  # True value
            return tokens

        context.pop()  # Drop the True value
        return parse_filtered_value_expr(context, tokens)
    else:
        raise ParserError('SyntaxError: expecting ELSE, got %s' % str(token))


def parse_exprs(context, tokens):
    while tokens:
        token = tokens[0]
        if token.type in VALUE_STARTING_TOKENS:
            tokens = parse_filtered_value_expr(context, tokens)
        elif token.type == Token.IF:
            tokens = parse_if_else(context, tokens[1:])
        else:
            raise ParserError('SyntaxError: expecting exprs, got %s' %
                              str(token))


def parse_root(context, tokens):
    parse_exprs(context, tokens)


def parse(template, variables):
    context = ParserContext(variables)
    tokens = tokenize(template)
    parse_root(context, tokens)
    return context.as_unicode_value()


def Render(template, variables):
    """Render template with variables."""
    if template is None:
        return None

    def replace(m):
        ret = parse(m.group(1), variables)
        return ret if ret else m.group(0)
    return HAS_VARIABLE_RE.sub(replace, to_unicode(template))
