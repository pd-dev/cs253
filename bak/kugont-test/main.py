#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import os
import re
import logging

rot13Html = '''
<html>
    <head>
        <title>Unit 2 Rot 13 homework</title>
    </head>

    <body>
        <h2>Enter some text to ROT13:</h2>
        <form method="post">
            <textarea name="text"
            style="height: 100px; width: 400px;">{filledText}</textarea>
            <br>
            <input type="submit">
        </form>
    </body>
</html>
'''

mainForm = '''
<br>
hello 小伙伴:
<br>
&nbsp;&nbsp;This is PD's web development test page!
<br><br>

<br>
<form action='http://www.google.com/search'>
	<input name="q" size=40>
	<input type="submit" value='google'>
</form>
<br>
<img src="/favicon.ico" alt="favicon"/>
<br>
<img src="/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine"/>
'''

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return re.match(USER_RE, username)

EMAIL_RE = re.compile(r"^([a-zA-Z0-9_-]{1,20})@([a-zA-Z0-9_-]{1,20})\.([a-zA-Z0-9_-]{1,20})$")
def valid_email(email):
    return re.match(EMAIL_RE, email)


htmlDir = os.path.join(os.path.dirname(__file__), 'html')
htmlSignUp = open(os.path.join(htmlDir, 'signup-form.html'), 'r').read()
htmlWelcome = open(os.path.join(htmlDir, 'welcome.html'), 'r').read()

def rot13(str):
    rot13str = ''
    for c in str:
        if c.isalpha():
            n = ord(c)
            if ((ord('A') <= n) and (n <= ord('M'))) or ((ord('a') <= n) and (n <= ord('m'))):
                rot13n = n+13
            else:
                rot13n = n-13
            rot13c = chr(rot13n)
        else:
            rot13c = c
        rot13str += rot13c
    return rot13str

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(mainForm)

class rot13Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write(rot13Html.format(filledText=''))

    def post(self):
    	text = self.request.get('text')
    	#rot13text = cgi.escape(rot13(text), quote=True)
        rot13text = cgi.escape(text.encode('rot13'), quote=True)
    	self.response.write(rot13Html.format(filledText=rot13text))

class signUpHandler(webapp2.RequestHandler):
    def get(self):
        user = ''
        email = ''
        info_user = ""
        info_pwd = ""
        info_verify = ""
        info_email = ""
        self.response.write(htmlSignUp.format(username=user,email=email,
            error_username=info_user, error_password=info_pwd, error_verify=info_verify, error_email=info_email))

    def post(self):
        user = self.request.get('username')
        pwd = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        info_user = ""
        info_pwd = ""
        info_verify = ""
        info_email = ""

        allValid = True
        if not valid_username(user):
            allValid = False
            info_user = "That's not a valid username."

        if not pwd:
            allValid = False
            info_pwd = "That wasn't a valid password."

        if pwd != verify:
            allValid = False
            info_verify = "Your passwords didn't match."

        if email and (not valid_email(email)):
            allValid = False
            info_email = "That's not a valid email"

        if allValid:
            self.redirect('/welcome'+'?username='+user)
        else:
            self.response.write(htmlSignUp.format(username=user,email=email,
                error_username=info_user, error_password=info_pwd, error_verify=info_verify, error_email=info_email))

class welcomeHandler(webapp2.RequestHandler):
    def get(self):
        user = self.request.get('username')
        self.response.write(htmlWelcome.format(username=user))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/rot13', rot13Handler),
    ('/signup', signUpHandler),
    ('/welcome', welcomeHandler)
], debug=True)
