#!/usr/bin/python
# -*- coding: utf-8 -*-

import want_ajax
import webapp2


app = webapp2.WSGIApplication([
      ('/want_ajax', want_ajax.WantAjax),
      ], debug=True)

