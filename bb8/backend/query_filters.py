# -*- coding: utf-8 -*-
"""
    Query Filters
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

FILTERS = {
    'str': str,
    'inc': lambda x: x + 1,
    'lower': lambda x: x.lower(),
    'upper': lambda x: x.upper(),
    'title': lambda x: x.title(),
}
