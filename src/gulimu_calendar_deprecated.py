'''
Created on 28 Sep 2010

@author: gulimujyujyu
'''
'''
Created on 27 Sep 2010

@author: gulimujyujyu
'''
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import users

import gdata
import gdata.calendar
import gdata.calendar.service
import gdata.alt.appengine

import os
import cgi
import atom
import logging
#import datetime
import constants
import urllib
import settings

# port
#port = os.environ['SERVER_PORT']
#if port and port != '80':
#    HOST_NAME = '%s:%s' % (os.environ['SERVER_NAME'], port)
#else:
#    HOST_NAME = os.environ['SERVER_NAME']

# data definition
class Event(db.Model):
    title = db.StringProperty(required=True)
    description = db.TextProperty()
    time = db.DateTimeProperty()
    location = db.TextProperty()
    creator = db.UserProperty()
    edit_link = db.TextProperty()
    gcal_event_link = db.TextProperty()
    gcal_event_xml = db.TextProperty()

class Attendee(db.Model):
    email = db.StringProperty()
    event = db.ReferenceProperty(Event)

class BasePage(webapp.RequestHandler):
    templateData = {
        'title':'calendar',
        };
    def __init__(self):
        # initialize the client
        #client = gdata.service.GDataService();
        self.client = gdata.calendar.service.CalendarService();
        gdata.alt.appengine.run_on_appengine(self.client);
        
    def get(self):
        #check if login
        if users.get_current_user():
            self.templateData['isLoggedIn'] = True;
            self.templateData['userLink'] = users.create_logout_url('/calendar');
        else :
            self.templateData['isLoggedIn'] = False;
            self.templateData['userLink'] = users.create_login_url('/');
        
        # get Feed Url
        feedUrl = self.request.get('feed_url');
        calendarID = self.request.get('calendarID');
        erase_tokens = self.request.get('erase_tokens')
        if erase_tokens:
            self.EraseStoredTokens()
        showXml = self.request.get('xml')
        if not feedUrl:
            if calendarID:
                feedUrl = 'https://www.google.com/calendar/feeds/default/' + calendarID + '/full';
            else:
                feedUrl = 'https://www.google.com/calendar/feeds/';
        
        # auth
        sessionToken = None;
        authToken = gdata.auth.extract_auth_sub_token_from_url(self.request.uri);
        authsub_token = self.request.get('token');
        self.templateData['authToken'] = authToken;
        self.templateData['authsub'] = authsub_token;
        if authToken:
            sessionToken = self.client.upgrade_to_session_token(authToken);
            self.client.SetAuthSubToken(sessionToken);
            self.templateData['sessionToken'] = sessionToken;
        else:
            auth_sub_url = self.client.GenerateAuthSubURL(self.request.uri, feedUrl,
                    secure=False, session=True)
            self.templateData['auth_sub_url'] = auth_sub_url;
            self.templateData['needAuth'] = True;
        
        if sessionToken and users.get_current_user():
            self.client.token_store.add_token(sessionToken);
            if isinstance(self.client.token_store.find_token(
                'https://www.google.com/calendar/feeds/'), gdata.auth.AuthSubToken) :
                feed = self.client.GetAllCalendarsFeed();
                self.templateData['feedsTitle'] = feed.title.text;
                self.templateData['feeds'] = feed.entry;
                self.templateData['needAuth'] = False;
        elif sessionToken :
            self.client.current_token = sessionToken;
            self.templateData['needAuth'] = True;
        else:
            next = atom.url.Url('http', settings.HOST_NAME, path='/calendar',
                    params={'feed_url': feedUrl})
            auth_sub_url = self.client.GenerateAuthSubURL(next, feedUrl,
                    secure=False, session=True)
            self.templateData['tokenRequestUrl'] = auth_sub_url;
            self.templateData['needAuth'] = True;
        
        self.templateData['feedUrl'] = feedUrl;
        self.FetchFeed(self.client, feedUrl, showXml)
        # Display the events.
        path = os.path.join(constants.Constants.TEMPLATE_PATH);
        path = os.path.join(path, 'calendar.html')
        self.response.out.write(template.render(path, self.templateData))
        
    def FetchFeed(self, client, feedUrl, showXml=False):
        try:
            if showXml :
                response = client.Get(feedUrl, converter=str)
                response = response.decode('UTF-8')
                self.response.out.write(cgi.escape(response))
            else:
                response = client.Get(feedUrl)
                if isinstance(response, atom.Feed):
                    self.RenderFeed(response)
                elif isinstance(response, atom.Entry):
                    self.RenderEntry(response)
                else:
                    self.response.out.write(cgi.escape(response.read()))
        except gdata.service.RequestError, request_error:
            # If fetching fails, then tell the user that they need to login to
            # authorize this app by logging in at the following URL.
            if request_error[0]['status'] == 401:
                # Get the URL of the current page so that our AuthSub request will
                # send the user back to here.
                next = atom.url.Url('http', settings.HOST_NAME, path='/calendar',
                    params={'feed_url': feedUrl})
                auth_sub_url = client.GenerateAuthSubURL(next, feedUrl,
                    secure=False, session=True)
                self.templateData['auth_sub_url'] = auth_sub_url;
                self.templateData['needAuth'] = True;
            else:
                self.templateData['errorStr'] = str(request_error[0]);
                self.templateData['haveError'] = True;
    
    def GetMoneyEntries(self, client, feedUrl, showXml=False, start_date='2010-07-01', end_date='2010-11-01'):
        try:
            if showXml :
                response = client.Get(feedUrl, converter=str)
                response = response.decode('UTF-8')
                self.response.out.write(cgi.escape(response))
            else:
                query = gdata.calendar.service.CalendarEventQuery('default', 'private', 'full');
                query.start_min = start_date;
                query.start_max = end_date; 

                feed = client.GetCalendarListFeed();
                
                self.templateData['events'] = feed.entry;
        except gdata.service.RequestError, request_error:
            # If fetching fails, then tell the user that they need to login to
            # authorize this app by logging in at the following URL.
            if request_error[0]['status'] == 401:
                # Get the URL of the current page so that our AuthSub request will
                # send the user back to here.
                next = atom.url.Url('http', settings.HOST_NAME, path='/calendar',
                    params={'feed_url': feedUrl})
                auth_sub_url = client.GenerateAuthSubURL(next, feedUrl,
                    secure=False, session=True)
                self.templateData['tokenRequestUrl'] = auth_sub_url;
                self.templateData['needAuth'] = True;
            else:
                self.templateData['errorStr'] = str(request_error[0]);
                self.templateData['haveError'] = True;
    
    def RenderFeed(self, feed):
        self.templateData['links'] = feed.link;
        self.templateData['entries'] = feed.entry;
    
    def RenderEntry(self, entry):
        self.templateData['entry'] = entry; 
        
    def DisplayAuthorizedUrls(self):
        tokens = gdata.alt.appengine.load_auth_tokens()
        self.templateData['tokens'] = tokens;
    
def main():
    application = webapp.WSGIApplication([('/.*', BasePage), ], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
