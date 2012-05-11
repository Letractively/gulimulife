'''
Created on 2011-4-10

@author: xiaolongzhu
'''
#!/usr/bin/python
#

import os

from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2
from django.template import loader as django_loader
import json as simplejson
from google.appengine.ext import db
from datetime import datetime

from utils import constants
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

#define entries
class Entry(db.Model):
    user = db.UserProperty(required=True);
    content = db.StringProperty(required=True);
    result = db.StringProperty();
    create_time = db.DateTimeProperty(required=True);
    finish_time = db.DateTimeProperty(required=True);
    category = db.IntegerProperty(required=True);

class UserDate(db.Model):
    user = db.UserProperty(required=True);
    date = db.DateTimeProperty(required=True);
    
tenthousand_prefix = '/tenthousand'

class MainPage(webapp2.RequestHandler):
    title = 'Main Page'
    
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri));
        
        template_values = {
            'user': users.get_current_user(),
        }

        self.response.out.write(django_loader.render_to_string('tenthousand/tenthousand.html', template_values));
        
    def post(self):
        self.get();

class FetchEntries(webapp2.RequestHandler):
    title = 'Fetch entries'
    
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
            
        try:
            results = db.GqlQuery("SELECT * FROM Entry WHERE user = :1",
                               users.get_current_user()) ###TODO
            
            json = []
            for entry in results:
                json.append({'entry_key': entry.key().__str__(),
                             'author': entry.user.nickname(),
                             'content': entry.content,
                             'result': entry.result,
                             'create_time': entry.create_time.isoformat(),
                             'finish_time': entry.finish_time.isoformat(),
                             'category': entry.category,
                             });
            json = [{'state': 200}, {'data': json}]
            self.response.out.write(simplejson.dumps(json))
        except webapp.RequestHandler.error:
            self.response.out.write("[{state:500}]")
            pass
        
    def post(self):
        self.get()
        
class FetchOneEntry(webapp2.RequestHandler):
    title = 'Fetch entries'
    
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
            
        try:
            entry_key = self.request.get('entry');
            entry = db.Key(entry_key);
        
            result = Entry.get(entry);
            
            if result:
                json = []
                json.append({'entry_key': result.key().__str__(),
                             'author': result.user.nickname(),
                             'content': result.content,
                             'result': result.result,
                             'create_time': result.create_time.isoformat(),
                             'finish_time': result.finish_time.isoformat(),
                             'category': result.category,
                             });
                self.response.out.write(simplejson.dumps(json))
                json = [{'state': 200}, {'data': json}]
            else:
                self.response.out.write("[{state:404}]")

        except webapp.RequestHandler.error:
            self.response.out.write("[{state:500}]")
            pass
    def post(self):
        self.get()
        
class AddOneEntry(webapp2.RequestHandler):
    title = 'Fetch entries'
    
    def get(self):
        self.post()
    
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
            
        try:
            entry_content = self.request.get('content');
            entry_category = int(self.request.get('category'));
            
            current_time = datetime.now();
            result = Entry(user=users.get_current_user(), 
                           content=entry_content,
                           create_time=current_time,
                           finish_time=current_time,
                           category=entry_category )
            result.put()
            
            json = []
            json.append({'entry_key': result.key().__str__(),
                         'author': result.user.nickname(),
                         'content': result.content,
                         'result': result.result,
                         'create_time': result.create_time.isoformat(),
                         'finish_time': result.finish_time.isoformat(),
                         'category': result.category,
                         });
            json = [{'state': 200}, {'data': json}]
            self.response.out.write(simplejson.dumps(json))

        except webapp.RequestHandler.error:
            self.response.out.write("[{state:500}]")
            pass

class PostOneEntry(webapp2.RequestHandler):
    title = 'Fetch entries'
    
    def get(self):
        self.post()
    
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
            
        try:
            entry_key = self.request.get('entry');
            entry_result = self.request.get('result');
            entry_finish = int(self.request.get('finish'));
            entry_content = self.request.get('content');
            entry_category = int(self.request.get('category'));
            
            entry = db.Key(entry_key);
        
            result = Entry.get(entry);
            
            if result:
                if entry_finish == 1:
                    result.finish_time = datetime.now()
                else:
                    result.finish_time = result.create_time;
                if entry_result:
                    result.result = entry_result
                if entry_content:
                    result.content = entry_content
                if entry_category:
                    result.category = entry_category
                
                result.put();
                    
                json = []
                json.append({'entry_key': result.key().__str__(),
                             'author': result.user.nickname(),
                             'content': result.content,
                             'result': result.result,
                             'create_time': result.create_time.isoformat(),
                             'finish_time': result.finish_time.isoformat(),
                             'category': result.category,
                             });
                json = [{'state': 200}, {'data': json}]
                self.response.out.write(simplejson.dumps(json))
            else:
                self.response.out.write("[{state:404}]")

        except webapp.RequestHandler.error:
            self.response.out.write("[{state:500}]")
            pass

class DeleteOneEntry(webapp2.RequestHandler):
    title = 'Fetch entries'
    
    def get(self):
        self.post()
    
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
            
        try:
            entry_key = self.request.get('entry');
            
            entry = db.Key(entry_key);
        
            result = Entry.get(entry);
            
            if result:
                result.delete();
                    
                json = []
                json.append({'entry_key': result.key().__str__(),
                             'author': result.user.nickname(),
                             'content': result.content,
                             'result': result.result,
                             'create_time': result.create_time.isoformat(),
                             'finish_time': result.finish_time.isoformat(),
                             'category': result.category,
                             });
                json = [{'state': 200}, {'data': json}]
                self.response.out.write(simplejson.dumps(json))
            else:
                self.response.out.write("[{state:404}]")

        except webapp.RequestHandler.error:
            self.response.out.write("[{state:500}]")
            pass

class ErrorPage(webapp2.RequestHandler):
    
    def get(self):
        template_dict = {
            "error_source": "TenThousand"};
        self.response.out.write(django_loader.render_to_string('404.html', template_dict));

#manage links
app = webapp2.WSGIApplication([(tenthousand_prefix, MainPage),
                                          (tenthousand_prefix + '/fetch_all_entries', FetchEntries),
                                          (tenthousand_prefix + '/fetch_one_entry', FetchOneEntry),
                                          (tenthousand_prefix + '/add_one_entry', AddOneEntry),
                                          (tenthousand_prefix + '/post_one_entry', PostOneEntry),
                                          (tenthousand_prefix + '/delete_one_entry', DeleteOneEntry),
                                          (tenthousand_prefix + '.*', ErrorPage)],
                                         debug=True)

