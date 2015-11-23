#!/usr/bin/env python
#

import webapp2

from jinja2helper import JHandler
from staticPage import *
from blogHandler import *
from wikiHandler import *






class mainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello!<br>Welcome to this ugly page...')






PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

app = webapp2.WSGIApplication([
    ('/', mainHandler),
    ('/blog', blogHandler),
    ('/blog/newpost', blogNewPostHandler),
    ('/blog/signup', blogSignupHandler),
    ('/blog/(\d+)', blogPostHandler),
    ('/blog/\.json', blogJsonHandler),
    ('/blog/(\d+)\.json', blogPostJsonHandler),
    ('/blog/welcome', blogWelcomHandler),
    ('/blog/login', blogLoginHandler),
    ('/blog/logout', blogLogoutHandler),
    ('/blog/flush', blogFlushHandler),

    ('/wiki/signup', wikiSignup),
    ('/wiki/login', wikiLogin),
    ('/wiki/logout', wikiLogout),
    ('/wiki/_edit' + PAGE_RE, wikiEditPage),
    ('/wiki' + PAGE_RE, wikiPage),
    ('/wiki', wikiRootPage),

    ('/radio', radioHandler),
    ('/google', googleHandler),
    ('/test1', ShowRequest),
    ('/rot13', rot13Handler),
    ('/fizzbuzz', FizzBuzzHandler),
    ('/signup', staticSignUpHandler),
    ('/welcome', welcomeHandler)
], debug=True)
