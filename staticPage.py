#!/usr/bin/env python
#

import os
import re
import webapp2
import cgi

from jinja2helper import JHandler


htmlPath = os.path.join(os.path.dirname(__file__), 'html')
print htmlPath
htmlSignUp = open(os.path.join(htmlPath, 'signup-form.html'), 'r').read()
htmlWelcome = open(os.path.join(htmlPath, 'welcome.html'), 'r').read()


htmlContent = '''
<form action="/test1">
    <input type="radio" name="r" value="one">
    <input type="radio" name="r" value="two">
    <input type="radio" name="r" value="three">
    <input type="submit">
</form>
'''

googlePage = '''
<form action="http://www.google.com/search">
    <input name="q">
    <input type="submit">
</form>
'''

rot13Page = '''
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


#url: /radio
class radioHandler(webapp2.RequestHandler):
    def get(self):
        #self.response.write('Hello, Udacity!')
        self.response.write(htmlContent)

#url: /google
class googleHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(googlePage)

#url: /test1
class ShowRequest(webapp2.RequestHandler):
    def get(self):
        #q = self.request.get("q")
        #self.response.write(q)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(self.request)

#url: /rot13
class rot13Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write(rot13Page.format(filledText=''))

    def post(self):
        text = self.request.get('text')
        rot13text = cgi.escape(text.encode('rot13'), quote=True)
        self.response.write(rot13Page.format(filledText=rot13text))

#url: /fizzbuzz
class FizzBuzzHandler(JHandler):
    def get(self):
        n = self.request.get('n', 0)
        n = n and int(n)
        self.render('fizzbuzz.html', n = n)

#url: /signup
class staticSignUpHandler(webapp2.RequestHandler):

    def valid_username(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return re.match(USER_RE, username)

    def valid_email(self, email):
        EMAIL_RE = re.compile(r"^([a-zA-Z0-9_-]{1,20})@([a-zA-Z0-9_-]{1,20})\.([a-zA-Z0-9_-]{1,20})$")
        return re.match(EMAIL_RE, email)

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
        if not self.valid_username(user):
            allValid = False
            info_user = "That's not a valid username."

        if not pwd:
            allValid = False
            info_pwd = "That wasn't a valid password."

        if pwd != verify:
            allValid = False
            info_verify = "Your passwords didn't match."

        if email and (not self.valid_email(email)):
            allValid = False
            info_email = "That's not a valid email"

        if allValid:
            self.redirect('/welcome'+'?username='+user)
        else:
            self.response.write(htmlSignUp.format(username=user,email=email,
                error_username=info_user, error_password=info_pwd, error_verify=info_verify, error_email=info_email))

#url: /welcome
class welcomeHandler(webapp2.RequestHandler):
    def get(self):
        user = self.request.get('username')
        self.response.write(htmlWelcome.format(username=user))