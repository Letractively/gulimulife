'''
Created on 2011-09-01

@author: gulimujyujyu
'''
#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging
from urlparse import urlparse
from urlparse import urljoin

from google.appengine.api import users
import webapp2
from django.template import loader as django_loader

import gdata
import gdata.calendar
import gdata.calendar.client
import time

from utils import constants

##Globals
AUTH_SETTINGS = {
    'APP_NAME': 'gulimulife-hr',
    'CONSUMER_KEY': 'life.gulimujyujyu.me',
    'CONSUMER_SECRET': 'NiKo8kYB7r-lUAAynbQWUUu7',
    'SIG_METHOD': gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
    'SCOPES': 'https://www.google.com/calendar/feeds/',
    }

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

gcal = gdata.calendar.client.CalendarClient()

everyday_prefix = '/everyday'

#main page
class MainPage(webapp2.RequestHandler):
    title = 'Main Page'

    # GET /
    def get(self):
        current_user = users.get_current_user()
        if not current_user:
            self.redirect(users.create_login_url(self.request.uri))

        access_token = gdata.gauth.AeLoad('accessKey')
        logging.info('Access Token:' + str(access_token))
        action_list = []

        if isinstance(access_token, gdata.gauth.OAuthHmacToken):
            #feed = gcal.GetCalendarListFeed()
            #action_list.append({'action_name':'Revoke token','action_content':everyday_prefix+'/revoke_token'})
            form_action = everyday_prefix + '/fetch_data'
            form_value = 'Now fetch my calendars!'
            revoke_token_link = True
        else:
            action_list.append({'action_name': 'Authorize', 'action_content': everyday_prefix + '/apply_oauth_token'})
            form_action = everyday_prefix + '/get_oauth_token'
            form_value = 'Give this website access to my Google Calendars'
            revoke_token_link = None

        converter_url = "\"" + everyday_prefix + '/currency_converter' + "\""

        template_values = {
            'form_action': form_action,
            'converter_url': converter_url,
            'form_value': form_value,
            'user': current_user,
            'user_nickname': current_user.nickname(),
            'action_list': action_list,
            'revoke_token_link': revoke_token_link,
            'access_token': access_token,
            }

        self.response.out.write(django_loader.render_to_string('everyday/soc.html', template_values))

#OAuth authorize
class OAuthApply(webapp2.RequestHandler):
    def get(self):
        """Fetches a request token and redirects the user to the approval page."""

        if users.get_current_user():
            # 1.) REQUEST TOKEN STEP. Provide the data scope(s) and the page we'll
            # be redirected back to after the user grants access on the approval page.

            uri_cur = urlparse(self.request.uri)
            #logging.info(self.request.uri)
            #logging.info(uri_cur)
            #logging.info(uri_cur.hostname)
            callback_url = urljoin(self.request.uri, 'get_oauth_token')
            #logging.info(callback_url)
            req_token = gcal.GetOAuthToken(
                scopes=AUTH_SETTINGS['SCOPES'], next=callback_url, consumer_key=AUTH_SETTINGS['CONSUMER_KEY'],
                consumer_secret=AUTH_SETTINGS['CONSUMER_SECRET'])

            # When using HMAC, persist the token secret in order to re-create an
            # OAuthToken object coming back from the approval page.
            gdata.gauth.AeSave(req_token, 'myKey')

            # Generate the URL to redirect the user to.  Add the hd paramter for a
            # better user experience.  Leaving it off will give the user the choice
            # of what account (Google vs. Google Apps) to login with.
            domain = self.request.get('domain', default_value='default')
            logging.info(domain)
            approval_page_url = req_token.generate_authorization_url(google_apps_domain=domain)
            logging.info('Request page 1: ' + str(approval_page_url))
            #logging.info('Request page 2: ' + gcal.GenerateOAuthAuthorizationURL(
            #    extra_params={'hd': domain}, callback_url=callback_url))

            # 2.) APPROVAL STEP.  Redirect to user to Google's OAuth approval page.
            logging.info(domain)
            logging.info(approval_page_url)
            self.redirect(str(approval_page_url))

#OAuth Handler Class
class OAuthFinish(webapp2.RequestHandler):
    """Handler for the 3 legged OAuth dance, v1.0a."""

    """This handler is responsible for fetching an initial OAuth request token,
      redirecting the user to the approval page.  When the user grants access, they
      will be redirected back to this GET handler and their authorized request token
      will be exchanged for a long - lived access token."""

    # GET /get_oauth_token
    def get(self):
        """Invoked after we're redirected back from the approval page."""

        saved_request_token = gdata.gauth.AeLoad('myKey')
        oauth_token = gdata.gauth.AuthorizeRequestToken(saved_request_token, self.request.uri)
        if oauth_token:
            access_token = gcal.GetAccessToken(oauth_token)
            gdata.gauth.AeSave(access_token, 'accessKey')

        self.redirect(everyday_prefix)

#Fetch Calendars Feed

#404 page
class ErrorPage(webapp2.RequestHandler):
    def get(self):
        template_dict = {
            "error_source": "Everyday"};
        self.response.out.write(django_loader.render_to_string('404.html', template_dict));

#manage links
app = webapp2.WSGIApplication([(everyday_prefix, MainPage),
    (everyday_prefix + '/apply_oauth_token', OAuthApply),
    (everyday_prefix + '/get_oauth_token', OAuthFinish),
    (everyday_prefix + '.*', ErrorPage)],
                                        debug=True)

