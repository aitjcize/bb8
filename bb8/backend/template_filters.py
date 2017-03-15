# -*- coding: utf-8 -*-
"""
    Query Filters
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

FILTERS = {
    'str': str,
    'int': int,
    'float': float,
    'inc': lambda x: x + 1,
    'lower': lambda x: x.lower(),
    'upper': lambda x: x.upper(),
    'title': lambda x: x.title(),
    'truncat': lambda l: lambda x: x[:l],  # pylint: disable=E0602
    # pylint: disable=E0602
    'unref': lambda def_val: lambda x: x if x is not None else def_val
}
