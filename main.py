#!/usr/bin/env python
#

import webapp2

from jinja2helper import JHandler
from staticPage import *
from blogHandler import *






class mainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello!<br>Welcome to this ugly page...')








app = webapp2.WSGIApplication([
    ('/', mainHandler),
    ('/blog', blogHandler),
    ('/blog/newpost', blogNewPostHandler),
    ('/blog/signup', blogSignupHandler),
    ('/blog/(\d+)', blogPostHandler),
    ('/blog/welcome', blogWelcomHandler),
    ('/blog/login', blogLoginHandler),
    ('/blog/logout', blogLogoutHandler),
    ('/radio', radioHandler),
    ('/google', googleHandler),
    ('/test1', ShowRequest),
    ('/rot13', rot13Handler),
    ('/fizzbuzz', FizzBuzzHandler),
    ('/signup', signUpHandler),
    ('/welcome', welcomeHandler)
], debug=True)
