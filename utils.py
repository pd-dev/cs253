


import hmac
import hashlib
import random
import re
import string
from datetime import datetime

from google.appengine.api import memcache


#######################################

cookie_secret = 'udacity_cs253_homework_final'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(cookie_secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(string.letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '{0}|{1}'.format(h, salt)

def valid_pw(name, password, h):
    split_list = h.split('|')
    if 2 != len(split_list):
        return False
    salt = split_list[1]
    return h == make_pw_hash(name, password, salt)

#######################################

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

#######################################

def age_set(key, val):
    save_time = datetime.utcnow()
    memcache.set(key, (val, save_time))

def age_get(key):
    r = memcache.get(key)
    if (r is not None):
        val, save_time = r
        age = (datetime.utcnow() - save_time).total_seconds()
    else:
        val, save_time = None, 0
    return val, save_time

def age_delete(key):
    memcache.delete(key)

#######################################

