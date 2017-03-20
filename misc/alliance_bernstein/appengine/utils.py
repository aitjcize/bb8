#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

def Unicode(s):
  """Convert s into unicode no matter it is str or unicode.

  Args:
    s: utf-8 str or unicode

  Returns:
    unicode
  """
  if isinstance(s, str):
    return s.decode('utf-8')
  elif isinstance(s, unicode):
    return s
  else:
    raise ValueError('Unsupported type: %s %r', type(s), s)

# Returns user's languages.
#
# Examples from HTTP headers:
#   en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4
#     ==>
#   [["en-US", "1.0"], ["en", "0.8"], ["zh-TW", "0.6"], ["zh", "0.4"]]
#
# Args:
#   self: the HTTP Reuqest object.
def getAcceptLanguage(self):
  langs = []

  lang_str = self.request.headers.get('accept_language', 'en')
  logging.debug('lang_str=%s' % lang_str)
  for pair in lang_str.split(","):
    lang = pair.split(";")
    if len(lang) < 2:
      lang.append("1.0")
    else:
      lang[1] = lang[1].split("=")[1]
    logging.debug("LANG=%s, q=%s" % (lang[0], lang[1]))
    langs.append(lang)

  return langs

def canonize_locale(lang):
  return lang.replace('-', '_')
