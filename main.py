#!/usr/bin/env python
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
import os
import logging
import cgi
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb

def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)

def get_email():
  email = None
  user = users.get_current_user()
  if user:
    email = user.email()
  return email

class Account(ndb.Model):
  name = ndb.StringProperty()
  hobby_text = ndb.StringProperty()
  modified = ndb.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
      #user_email = get_email()
      user = users.get_current_user()
      if user:
        # fetch the user from the database
        user_key = ndb.Key("Account", user.user_id())
        user_account = user_key.get()
        #If the user isn't found in the database, add to the database
        if not user_account:
          logging.info("USER NOT FOUND, ADDING NOW")
          user_account = Account(id=user.user_id(), name = user.nickname(), hobby_text = '')
          user_key = user_account.put()
        else:
          logging.info("USER FOUND")
          logging.info(user_account)

        # Redirect to the user's view profile page
        self.redirect('/viewprofile?id=' + user.user_id())
        template_params = {
        "user":user.email(),
        "login":users.create_login_url(),
        "logout":users.create_logout_url('/'),
        "name":user_account.name,
        "hobby":user_account.hobby_text,
        "modified":user_account.modified
        }
      else:
        logging.info("NOT LOGGED IN")
        template_params = {
        "user":None,
        "login":users.create_login_url('/'),
        "logout":users.create_logout_url('/')
        }
        render_template(self, 'index.html', template_params)

class viewprofileHandler(webapp2.RequestHandler):
  def get(self):
    #get the id of the user whose page we want to view
    id_param = self.request.get('id')

    #get that user from the database
    user_key = ndb.Key("Account", id_param)
    user_info = user_key.get()

    #If that user doesn't exist in the database, show an error
    if not user_info:
      self.redirect('/notfound.html')
    
    #otherwise, show that user's information

    template_params = {
    "user":get_email(),
    "login":users.create_login_url(),
    "logout":users.create_logout_url('/'),
    "name":user_info.name,
    "hobby":user_info.hobby_text,
    "modified":user_info.modified
    }

    render_template(self, 'viewprofile.html', template_params)

class editprofileHandler(webapp2.RequestHandler):
  def get(self):
    #user_email = get_email()
      user = users.get_current_user()
      if user:
        # fetch the user from the database
        user_key = ndb.Key("Account", user.user_id())
        user_account = user_key.get()

        template_params = {
        "user":user.email(),
        "login":users.create_login_url(),
        "logout":users.create_logout_url('/'),
        "name":user_account.name,
        "hobby":user_account.hobby_text,
        "modified":user_account.modified
        }

        render_template(self, 'editprofile.html', template_params)

class editedHandler(webapp2.RequestHandler):
  def post(self):
    name=cgi.escape(self.request.get("name"))
    hobby = cgi.escape(self.request.get("hobby"))

    user = users.get_current_user()
    if not user:
      self.redirect('/')
    user_key = ndb.Key("Account", user.user_id())
    user_account = Account(id=user.user_id(), name = name, hobby_text = hobby)
    user_account.put()

    self.redirect("/viewprofile?id=" + user.user_id())


mappings = [
  ('/', MainHandler),
  ('/viewprofile', viewprofileHandler),
  ('/editprofile', editprofileHandler),
  ('/edit', editedHandler)
  ]
app = webapp2.WSGIApplication(mappings, debug=True)