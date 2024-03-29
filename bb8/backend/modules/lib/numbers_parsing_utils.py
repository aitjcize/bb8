# -*- coding: utf-8 -*-
"""
    Numbers Parsing Utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

NUMBER_DICT = {
    u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6,
    u'七': 7, u'八': 8, u'九': 9, u'十': 10, u'百': 100, u'千': 1000,
    u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4, u'５': 5, u'６': 6,
    u'７': 7, u'８': 8, u'９': 9,
    u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4, u'伍': 5, u'陆': 6, u'陸': 6,
    u'柒': 7, u'捌': 8, u'玖': 9, u'拾': 10, u'佰': 100
}


def convert_to_arabic_numbers(number_char):
    """Convert various types of numbers representation to arabic numbers."""
    if not isinstance(number_char, unicode):
        number_char = unicode(number_char, 'utf8')

    try:
        return int(number_char, base=10)
    except ValueError:
        pass

    digit = 0
    tmp = 0
    for orig_char in number_char:
        tmp_number = NUMBER_DICT.get(orig_char, None)
        if tmp_number is None:
            raise RuntimeError('Got invalid mandarin')
        if tmp_number >= 10:
            if tmp == 0:
                tmp = 1
            digit = digit + tmp_number * tmp
            tmp = 0
        elif tmp_number is not None:
            tmp = tmp * 10 + tmp_number
    digit = digit + tmp
    return digit
