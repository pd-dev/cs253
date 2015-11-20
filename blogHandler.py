#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


import re
import time
import random
import string
import json
import hmac
import hashlib
import logging
import time
import datetime
from google.appengine.api import memcache
from google.appengine.ext import db


from jinja2helper import JHandler


class BlogData(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class BlogUser(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    psw_hash = db.StringProperty(required=True)
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add=True)


#####################################################

cookie_secret = 'my_homework'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(cookie_secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name+pw+salt).hexdigest()
    return '{0}|{1}'.format(h, salt)


def valid_pw(name, pw, h):
    split_list = h.split('|')
    if 2 != len(split_list):
        return False
    salt = split_list[1]
    return (h == make_pw_hash(name, pw, salt))


#####################################################


class blogBaseHandler(JHandler):
    def blogSubmit(self, blogs=iter([])):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if not (subject and content):
            self.render_main(subject, content, "标题内容都要写 - need both subject & content", blogs=blogs)
            return

        blog = BlogData(subject=subject, content=content)
        blog.put()

        time.sleep(0.1) # the datastore may not updated right after put()

        self.getBlogs(True)

        return blog

    def getBlog(self, postId, update=False):
        blogkey = 'blog_post_'+postId
        blogUpdatekey = 'blog_updated_'+postId
        blog = memcache.get(blogkey)
        if ((blog is None) or update):
            getStr = "select * from BlogData where __key__ = KEY('BlogData', {id})".format(id=postId)
            blogs = db.GqlQuery(getStr)
            if 0 == blogs.count():
                return None, ''
            blog = blogs[0]
            memcache.set(blogkey, blog)
            memcache.set(blogUpdatekey, time.time())
        lastUpdate = time.time()-memcache.get(blogUpdatekey)
        return blog, str(lastUpdate)

    def getBlogs(self, update=False):
        key = 'top_blogs'

        blogs = memcache.get(key)
        if ((blogs is None) or update):
            getStr = "select * from BlogData order by created desc limit 20"
            blogs = db.GqlQuery(getStr)
            blogs = list(blogs)
            memcache.set(key, blogs)

            # update time
            memcache.set('top_blogs_last_update', time.time())
        lastUpdate = time.time()-memcache.get('top_blogs_last_update')
        return blogs, str(lastUpdate)


class blogHandler(blogBaseHandler):
    def render_main(self, subject='', content='', error='', blogs=iter([]), last_update=''):
        self.render('blog-main.html', subject=subject, content=content, error=error.decode("utf-8"), blogs=blogs, last_update=last_update)

    def get(self):
        blogs, lastUpdate = self.getBlogs()
        self.render_main(blogs=blogs, last_update=lastUpdate)

    def post(self):
        blogs, lastUpdate = self.getBlogs()

        blog = self.blogSubmit(blogs)

        blog_id = blog.key().id()
        post_path = '/blog/'+str(blog_id)

        self.redirect(post_path)


class blogNewPostHandler(blogBaseHandler):
    def render_main(self, subject='', content='', error='', last_update='0'):
        self.render('blog-main.html', subject=subject, content=content, error=error.decode("utf-8"), last_update=last_update)

    def get(self):
        self.render_main()

    def post(self):
    	blog = self.blogSubmit()

        blog_id = blog.key().id()
        post_path = '/blog/'+str(blog_id)

        self.redirect(post_path)


class blogPostHandler(blogBaseHandler):
    def get(self, id):
        blog, last_update = self.getBlog(id)

        if None == blog:
            self.response.write("You are not supposed to be here... "+id)
            return

        self.render('blog-post.html', blogs=[blog], last_update=last_update)


class blogJsonHandler(blogBaseHandler):
    def getJsonbyBlogs(self, blogs):
        jsonList = []
        for blog in blogs:
            jsonDict = {}
            jsonDict['subject'] = blog.subject
            jsonDict['content'] = blog.content
            jsonDict['created'] = blog.created.strftime('%a %b %d %H:%M:%S %Y')

            jsonList.append(jsonDict)
        return json.dumps(jsonList, encoding='utf-8')

    def get(self):
        getStr = "select * from BlogData order by created desc limit 20"
        blogs = db.GqlQuery(getStr)

        blog = blogs[0]
        jsonString = self.getJsonbyBlogs(blogs)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(jsonString)
        return


class blogPostJsonHandler(blogBaseHandler):
    def get(self, postId):
        postId = postId.split('.')[0]
        #5733953138851840

        blog, last_update = self.getBlog(postId)

        if None == blog:
            self.response.write("You are not supposed to be here... "+postId)
            return

        jsonObject = {}
        jsonObject['subject'] = blog.subject
        jsonObject['content'] = blog.content
        jsonObject['created'] = blog.created.strftime('%a %b %d %H:%M:%S %Y')

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(jsonObject, encoding='utf-8'))
        return


# /blog/signup
class blogSignupHandler(blogBaseHandler):
    def render_page(self, username='', email='', error_username='', error_password='', error_verify='', error_email=''):
        self.render('blog-signup.html', username=username, email=email,
         error_username=error_username, error_password=error_password, error_verify=error_verify, error_email=error_email)

    def valid_username(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return re.match(USER_RE, username)

    def valid_email(self, email):
        EMAIL_RE = re.compile(r"^([a-zA-Z0-9_-]{1,20})@([a-zA-Z0-9_-]{1,20})\.([a-zA-Z0-9_-]{1,20})$")
        return re.match(EMAIL_RE, email)

    def get(self):
        self.render_page()

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
            getStr = "select * from BlogUser where username='{username}'".format(username=user)
            db_users = db.GqlQuery(getStr)
            if db_users.count() > 0:
                info_user = "That user already exists."
                self.render_page(username=user, email=email, 
                    error_username=info_user, error_password=info_pwd, error_verify=info_verify, error_email=info_email)
            else:
                psw_hash = make_pw_hash(user, pwd)
                if email:
                    db_user = BlogUser(username=user, password=pwd, psw_hash=psw_hash, email=email)
                else:
                    db_user = BlogUser(username=user, password=pwd, psw_hash=psw_hash)
                db_user.put()

                self.set_cookie('user', make_secure_val(user))

                self.redirect('/blog/welcome')
        else:
            self.render_page(username=user, email=email, 
                error_username=info_user, error_password=info_pwd, error_verify=info_verify, error_email=info_email)

# /blog/welcome
class blogWelcomHandler(blogBaseHandler):
    def render_page(self, username=''):
        self.render('blog-welcome.html', username=username)

    def get(self):
        user = self.request.cookies.get('user')

        if (not user) or ('' == user):
            self.redirect('/blog/signup')
            return

        user = check_secure_val(user)
        if not user:
            self.redirect('/blog/signup')
        else:
            self.render_page(username=user)

# /blog/login
class blogLoginHandler(blogBaseHandler):
    def render_page(self, username='', error=''):
        self.render('blog-login.html', username=username, error=error)

    def get(self):
        self.render_page()

    def post(self):
        user = self.request.get('username')
        pwd = self.request.get('password')

        if not (user and pwd):
            self.render_page(username=user, error='Invalid login')
            return

        getStr = "select * from BlogUser where username='{username}'".format(username=user)
        db_users = db.GqlQuery(getStr)
        if 1 != db_users.count():
            self.render_page(username=user, error='Invalid login!')
            return

        blogUser = db_users.get()

        if not valid_pw(user, pwd, blogUser.psw_hash):
            self.render_page(username=user, error='Invalid login')
            return

        self.set_cookie('user', make_secure_val(user))
        self.redirect('/blog/welcome')

# /blog/logout
class blogLogoutHandler(blogBaseHandler):
    def get(self):
        self.set_cookie('user', '')
        self.redirect('/blog/signup')

# /blog/flush
class blogFlushHandler(blogBaseHandler):
    def get(self):
        memcache.flush_all()

        self.redirect('/blog')
        return


