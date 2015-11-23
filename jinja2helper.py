#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import json

import webapp2
import jinja2
from google.appengine.ext import db

from utils import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)



class JHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user    # user or None
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_cookie(self, name, value, path='/'):
        self.response.headers.add_header(
            'Set-Cookie',
            '{name}={value}; Path={path}'.format(name=name, value=value, path=path))

    def set_secure_cookie(self, name, value, path='/'):
        cookie_val = make_secure_val(value)
        self.response.headers.add_header(
            'Set-Cookie',
            '{name}={value}; Path={path}'.format(name=name, value=cookie_val, path=path))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)  # "a and b" returns b if a is True, else returns a

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.set_cookie('user_id', '')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

#######################################

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    ###
    db_group = 'default'
    db_path = 'users'

    @classmethod
    def users_key(cls):
        return db.Key.from_path(cls.db_path, cls.db_group)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = cls.users_key())

    @classmethod
    def by_name(cls, name):
        '''
        getStr = "select * from User where name='{name}'".format(name=user)
        db_users = db.GqlQuery(getStr)
        user = db_users.get()
        '''
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = cls.users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

#######################################

class SignupHandler(JHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

#######################################

