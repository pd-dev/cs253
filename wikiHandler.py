#!/usr/bin/env python
# -*- coding: utf-8 -*-
#



import logging
import time

from google.appengine.api import memcache
from google.appengine.ext import db

from utils import *
from jinja2helper import *


class WikiPage(db.Model):
    url = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    version = db.IntegerProperty(default = 0)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @staticmethod
    def parent_key(path):
        return db.Key.from_path('/wiki'+path, 'pages')

    @classmethod
    def by_path(cls, path):
        q = cls.all()
        q.ancestor(cls.parent_key(path))
        q.order("-created")
        return q

    @classmethod
    def by_id(cls, page_id, path):
        return cls.get_by_id(page_id, cls.parent_key(path))


class WikiUser(User):
    User.set_db_parent('default', 'wiki_users')
    #User.db_group = 'default'
    #User.db_path = 'wiki_users'



#####################################################

class wikiHandler(JHandler):
    def get_page(self, url, version=0, update=False):
        key_wikiPage = 'wikiPage/'+url

        pv, age = age_get(key_wikiPage)
        if pv is not None:
            p, get_ver = pv
        if ((pv is None) or update or ((0 != version) and (version != get_ver))):
            q = WikiPage.by_path(url)
            if (q is None) or (version > q.count()):
                return None, version, None

            get_ver = q.count() if (0 == version) else version
            p = q.get(offset=(q.count()-get_ver))

            # cache latest version
            if (get_ver == q.count()):
                pv = p, get_ver
                age_set(key_wikiPage, pv)
        return p, get_ver, age

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
            self.redirect('/wiki/')


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
        version = self.request.get('v')
        try:
            version = int(version)
        except Exception, e:
            version = 0
        p, ver, age = self.get_page(url, version=version)
        if p is None:
            content = ''
        else:
            content=p.content
        self.render('wiki-edit.html', url=url, content=content)

    def post(self, url):
        content = self.request.get('content')
        p, ver, age = self.get_page(url)

        if (p is None) or (p.content != content):
            p = WikiPage(url=url, content=content, parent=WikiPage.parent_key(url))
            p.put()

            time.sleep(0.2)
            self.get_page(url, update=True)

        self.redirect('/wiki'+url)
        return


# /wiki/*
class wikiPage(wikiHandler):
    def get(self, url):
        version = self.request.get('v')
        try:
            version = int(version)
        except Exception, e:
            version = 0
        p, ver, age = self.get_page(url, version=version)
        if p is None:
            self.redirect('/wiki/_edit'+url)
        else:
            self.render('wiki-view.html', url=url, content=p.content)
        return


# /wiki/
class wikiRootPage(wikiHandler):
    def get(self):
        self.redirect('/wiki/')
        return


# /wiki/_history/*
class wikiHistoryPage(wikiHandler):
    def get(self, url):
        pages = WikiPage.by_path(url).fetch(limit=None)

        for index, page in enumerate(pages):
            page.version = len(pages)-index
        self.render('wiki-history.html', url=url, pages=pages)