#!/usr/bin/env python
# -*- coding: utf-8 -*-
#



import logging

from google.appengine.api import memcache
from google.appengine.ext import db

from utils import *
from jinja2helper import *


class WikiPage(db.Model):
    url = db.StringProperty(required = True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now = True)


class WikiUser(User):
    User.set_db_parent('default', 'wiki_users')
    #User.db_group = 'default'
    #User.db_path = 'wiki_users'



#####################################################

class wikiHandler(JHandler):
    def get_page(self, url, update=False):
        key_wikiPage = 'wikiPage/'+url

        p, age = age_get(key_wikiPage)
        if ((p is None) or update):
            p = WikiPage.all().filter('url =', url).get()
            age_set(key_wikiPage, p)
        return p, age

    def set_page(self, page):
        page.put()
        key_wikiPage = 'wikiPage/'+page.url
        age_set(key_wikiPage, page)
        return

    def set_referer(self, referer):
        age_set('wikiReferer', referer)

    def get_referer(self):
        referer, age = age_get('wikiReferer')
        return referer, age


# /wiki/signup
class wikiSignup(SignupHandler):
    def done(self):
        #make sure the user doesn't already exist
        u = WikiUser.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = WikiUser.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/wiki')


# /wiki/login
class wikiLogin(wikiHandler):
    def get(self):
        self.set_referer(self.getReferer())
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            referer, _ = self.get_referer()
            self.redirect(referer if referer is not None else '/wiki/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)


# /wiki/logout
class wikiLogout(wikiHandler):
    def get(self):
        referer = self.getReferer()

        self.logout()
        self.redirect(referer if referer is not None else '/wiki/')


# /wiki/_edit/*
class wikiEditPage(wikiHandler):
    def get(self, url):
        p, age = self.get_page(url)
        if p is None:
            content = ''
        else:
            content=p.content
        self.render('wiki-edit.html', url=url, content=content)

    def post(self, url):
        content = self.request.get('content')
        p, age = self.get_page(url)
        if p is None:
            p = WikiPage(url=url, content=content)
        else:
            p.content = content
        self.set_page(p)

        # update may not work, cause a query() right after a put() may get None
        #p.put()
        #self.get_page(url, update=True)

        self.redirect('/wiki'+url)

        return


# /wiki/*
class wikiPage(wikiHandler):
    def get(self, url):
        p, age = self.get_page(url)
        if p is None:
            self.redirect('/wiki/_edit'+url)
        else:
            self.render('wiki-view.html', url=url, content=p.content)
        return


# /wiki/
class wikiRootPage(wikiHandler):
    def get(self):
        self.redirect('/wiki/')
