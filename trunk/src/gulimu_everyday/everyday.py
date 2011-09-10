'''
Created on 2011-09-01

@author: gulimujyujyu
'''
#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import logging

from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import oauth

import gdata
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom.data
import time

from utils import constants

##Globals
SETTINGS = {
  'APP_NAME': 'gulimulife',
  'CONSUMER_KEY': 'gulimulife.appspot.com',
  'CONSUMER_SECRET': 'P7ujwzNKRof2HmLS2L+Zj2zk',
  'SIG_METHOD': gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
  'SCOPES': 'https://www.google.com/calendar/feeds/',
  }

gcal = gdata.calendar.service.CalendarService()
#gcal = gdata.service.GDataService();
gcal.SetOAuthInputParameters(SETTINGS['SIG_METHOD'], SETTINGS['CONSUMER_KEY'],
                              consumer_secret=SETTINGS['CONSUMER_SECRET'])
gdata.alt.appengine.run_on_appengine(gcal)
everyday_prefix = '/everyday'

#main page
class MainPage(webapp.RequestHandler):
    title = 'Main Page'

    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri));

        try:
            user = oauth.get_current_user();
            oauth_key = oauth.get_oauth_consumer_key();
            logging.info(oauth_key);

        except oauth.OAuthRequestError:
            user = users.get_current_user();

        template_values = {
            'user': user,
        }

        #logging.info( constants.Constants.TEMPLATE_PATH)
        path = os.path.join(constants.Constants.TEMPLATE_PATH, 'everyday/everyday.html')
        self.response.out.write(template.render(path, template_values));

    def post(self):
        self.get();


#OAuth Handler Class
class OAuthDance(webapp.RequestHandler):

    """Handler for the 3 legged OAuth dance, v1.0a."""

    """This handler is responsible for fetching an initial OAuth request token,
      redirecting the user to the approval page.  When the user grants access, they
      will be redirected back to this GET handler and their authorized request token
      will be exchanged for a long - lived access token."""

    # GET /get_oauth_token
    def get(self):
        """Invoked after we're redirected back from the approval page."""

        self.session = Session()
        oauth_token = gdata.auth.OAuthTokenFromUrl(self.request.uri)
        if oauth_token:
            oauth_token.secret = self.session['oauth_token_secret']
            oauth_token.oauth_input_params = gcal.GetOAuthInputParameters()
            gcal.SetOAuthToken(oauth_token)

            # 3.) Exchange the authorized request token for an access token
            oauth_verifier = self.request.get('oauth_verifier', default_value='')
            access_token = gcal.UpgradeToOAuthAccessToken(
                oauth_verifier=oauth_verifier)

            # Remember the access token in the current user's token store
            if access_token and users.get_current_user():
                gcal.token_store.add_token(access_token)
            elif access_token:
                gcal.current_token = access_token
                gcal.SetOAuthToken(access_token)

        self.redirect(calendar_prefix)

    # POST /get_oauth_token
    def post(self):
        """Fetches a request token and redirects the user to the approval page."""

        self.session = Session()

        if users.get_current_user():
            # 1.) REQUEST TOKEN STEP. Provide the data scope(s) and the page we'll
            # be redirected back to after the user grants access on the approval page.
            req_token = gcal.FetchOAuthRequestToken(
                scopes=SETTINGS['SCOPES'], oauth_callback=self.request.uri)

            # When using HMAC, persist the token secret in order to re-create an
            # OAuthToken object coming back from the approval page.
            self.session['oauth_token_secret'] = req_token.secret

            # Generate the URL to redirect the user to.  Add the hd paramter for a
            # better user experience.  Leaving it off will give the user the choice
            # of what account (Google vs. Google Apps) to login with.
            domain = self.request.get('domain', default_value='default')
            approval_page_url = gcal.GenerateOAuthAuthorizationURL(
                extra_params={'hd': domain})

            # 2.) APPROVAL STEP.  Redirect to user to Google's OAuth approval page.
            self.redirect(approval_page_url)

#404 page
class ErrorPage(webapp.RequestHandler):

    def get(self):
        path = os.path.join(constants.Constants.TEMPLATE_PATH, '404.html');

        template_dict = {
            "error_source": "Everyday"};
        self.response.out.write(template.render(path, template_dict));

#manage links
def main():
    application = webapp.WSGIApplication([(everyday_prefix, MainPage),
                                          (everyday_prefix + '.*', ErrorPage)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
