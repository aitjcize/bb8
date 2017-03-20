from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
import webapp2
import json as simplejson

class AjaxHelper(webapp2.RequestHandler):
  """AJAX Helper class for callback

http://url_path/book?action=Add&name=xxx&id=yyy

import ajax_helper
import webapp2
from google.appengine.ext.webapp import util

class Book(ajax_helper.AjaxHelper):
  def __init__(self, request, response):
    self.initialize(request, response)
    ajax_helper.AjaxHelper.methods = self

  def Add(self):
    return {"msg": "completed", "code": 200}

  def Del(self):
    bid = self.request.get("bid")

app = webapp2.WSGIApplication([
    ('/book', Book),
    ], debug=True)
  """

  debug = False
  methods = None

  def __init__(self, request, response):
    self.initialize(request, response)

  def handle_request(self):
    func = None

    action = self.request.get("action")
    if action:
      if action[0] == "_":
        if self.debug:
          print "You are not allow not access this function: %s" % action
        self.error(403)  # access denied
        return
      else:
        func = getattr(self.methods, action, None)

    if not func:
      if self.debug:
        if not action: action = "None"
        print "action=%s is not found" % action
      self.error(404)  # file not found
      return

    result = func()
    self.response.headers.add_header('Content-type', 'application/json')
    if isinstance(result, basestring):
      self.response.out.write(result)  # func() has converted to JSON.
    else:
      self.response.out.write(simplejson.dumps(result))

  def get(self):
    self.handle_request()

  def post(self):
    self.handle_request()
