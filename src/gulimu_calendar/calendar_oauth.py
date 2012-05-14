'''
Created on 11 Oct 2010

@author: gulimujyujyu
'''
#!/usr/bin/python
#
# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0

import cgi
import re
import os
import gdata
import logging

import atom
import gdata
import gdata.calendar
import gdata.calendar.service
import gdata.alt
import gdata.alt.appengine

from appengine_utilities.gmemsess import Session
import json as simplejson
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
import webapp2
from google.appengine.api import urlfetch
from django.template import loader as django_loader

from utils import constants


AUTH_SETTINGS = {
    'APP_NAME': 'gulimulife-hr',
    'CONSUMER_KEY': 'life.gulimujyujyu.me',
    'CONSUMER_SECRET': 'NiKo8kYB7r-lUAAynbQWUUu7',
    'SIG_METHOD': gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
    'SCOPES': 'https://www.google.com/calendar/feeds/',
    }

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

gcal = gdata.calendar.service.CalendarService()
#gcal = gdata.service.GDataService();
gcal.SetOAuthInputParameters(AUTH_SETTINGS['SIG_METHOD'], AUTH_SETTINGS['CONSUMER_KEY'],
    consumer_secret=AUTH_SETTINGS['CONSUMER_SECRET'])
gdata.alt.appengine.run_on_appengine(gcal)

calendar_prefix = '/calendar'

class MainPage(webapp2.RequestHandler):
    title = 'MainPage'

    # GET /
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))

        access_token = gcal.token_store.find_token(AUTH_SETTINGS['SCOPES'])

        if isinstance(access_token, gdata.auth.OAuthToken):
            #feed = gcal.GetCalendarListFeed()

            form_action = calendar_prefix + '/fetch_data'
            form_value = 'Now fetch my calendars!'
            revoke_token_link = True
        else:
            form_action = calendar_prefix + '/get_oauth_token'
            form_value = 'Give this website access to my Google Calendars'
            revoke_token_link = None

        converter_url = '"' + calendar_prefix + '/currency_converter' + '"'
        template_values = {
            'form_action': form_action,
            'converter_url': converter_url,
            'form_value': form_value,
            'user': users.get_current_user(),
            'revoke_token_link': revoke_token_link,
            'oauth_token': access_token,
            'consumer': gcal.GetOAuthInputParameters().GetConsumer(),
            'sig_method': gcal.GetOAuthInputParameters().GetSignatureMethod().get_name()
        }

        self.response.out.write(django_loader.render_to_string("calendar/calendar.html", template_values))


class OAuthDance(webapp2.RequestHandler):
    """Handler for the 3 legged OAuth dance, v1.0a."""

    """This handler is responsible for fetching an initial OAuth request token,
      redirecting the user to the approval page.  When the user grants access, they
      will be redirected back to this GET handler and their authorized request token
      will be exchanged for a long - lived access token."""

    # GET /get_oauth_token
    def get(self):
        """Invoked after we're redirected back from the approval page."""

        self.session = Session(self)
        #logging.warning(self.session.cookie.output())

        oauth_token = gdata.auth.OAuthTokenFromUrl(self.request.uri)
        if oauth_token:
            #logging.warning(oauth_token)
            #logging.warning(self.session.__str__())
            #logging.warning(self.session.cookie.output())
            oauth_token.secret = self.session['oauth_token_secret']
            #logging.warning(self.session['oauth_token_secret'])
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

        self.session = Session(self)
        #logging.warning(self.session.cookie.output())

        if users.get_current_user():
            # 1.) REQUEST TOKEN STEP. Provide the data scope(s) and the page we'll
            # be redirected back to after the user grants access on the approval page.
            req_token = gcal.FetchOAuthRequestToken(
                scopes=AUTH_SETTINGS['SCOPES'], oauth_callback=self.request.uri)

            # When using HMAC, persist the token secret in order to re-create an
            # OAuthToken object coming back from the approval page.
            #logging.warning(req_token.secret)
            self.session['oauth_token_secret'] = req_token.secret
            self.session.save()
            #logging.warning(self.session['oauth_token_secret'])
            #logging.warning(self.session.keys())
            #logging.warning(self.session.cookie.output())

            # Generate the URL to redirect the user to.  Add the hd paramter for a
            # better user experience.  Leaving it off will give the user the choice
            # of what account (Google vs. Google Apps) to login with.
            domain = self.request.get('domain', default_value='default')
            approval_page_url = gcal.GenerateOAuthAuthorizationURL(
                extra_params={'hd': domain})

            # 2.) APPROVAL STEP.  Redirect to user to Google's OAuth approval page.
            self.redirect(approval_page_url)


class FetchData(OAuthDance):
    """Fetches the user's data."""

    """This class inherits from OAuthDance in order to utilize OAuthDance.post()
      in case of a request error (e.g. the user has a bad token)."""

    # GET /fetch_data
    def get(self):
        self.post()
        #self.redirect(calendar_prefix)

    # POST /fetch_data
    def post(self):
        """Fetches the user's data."""

        calendarId = self.request.get('calId');
        projection = self.request.get('proj', default_value=constants.Constants.CAL_PROJECTION);
        start_min = self.request.get('start-min', default_value=constants.Constants.CAL_START)
        start_max = self.request.get('start-max', default_value=constants.Constants.CAL_END)
        max_results = self.request.get('max-results', default_value=constants.Constants.CAL_MAX_RESULTS)

        feed_url = constants.Constants.CAL_FEEDURL + calendarId + projection\
                   + '?start-min=' + start_min + '&start-max=' + start_max\
                   + '&max-results=' + max_results;
        #feed_url = 'https://www.google.com/calendar/feeds/default/owncalendars/full/'
        #feed_url = 'https://www.google.com/calendar/feeds/15k5jcgdnscdj9j5lposl32hms%40group.calendar.google.com/private/full'
        try:
            json = [];

            response = gcal.Get(feed_url)
            ##logging.warning("INFO:\t\t\tEntry:" + str(response))
            # for xml
            #response = gcal.Get(feed_url, converter=str)
            #self.response.out.write(response)javascript:;
            if isinstance(response, atom.Feed):
                reg = re.compile(r"^[\w.]+[\|]{2}[A-Z]{3}[\d.]+([$]{2}(\w+[,;]?)+)?$")
                for entry in response.entry:
                    tmpWhen = None
                    for lala in entry.extension_elements:
                        if lala.tag == 'when':
                            tmpWhen = lala.attributes
                    if tmpWhen is None:
                        startTime = ''
                    else:
                        startTime = tmpWhen.get('startTime')

                    #logging.info(entry.title.text)
                    if reg.match(entry.title.text):
                        #logging.info('Pass the re:'+entry.title.text)
                        json.append({'title': entry.title.text,
                                     'links': {'alternate': entry.GetHtmlLink().href},
                                     'published': entry.published.text,
                                     'startTime': startTime,
                                     'updated': entry.updated.text,
                                     })
            #    json = [{"state":"Feed Format"}];
            elif isinstance(response, atom.Entry):
                json = {'title': response.title.text}
            #    json = [{"state":"Entry Format"}];
            else:
                json = {"state": "Unknown Format"}

                #feed = gcal.GetCalendarListFeed()

                #for entry in feed.entry:
                #json.append({'title': entry.title.text,
                #    })
            self.response.out.write(simplejson.dumps(json))
        except gdata.service.RequestError, error:
            json = {"error": 'Unkown Error'};
            self.response.out.write(simplejson.dumps(json))
            pass
            #OAuthDance.post(self)


class FetchCalendar(OAuthDance):
    """Fetches the user's calendar."""

    """This class inherits from OAuthDance in order to utilize OAuthDance.post()
      in case of a request error (e.g. the user has a bad token)."""

    # GET /fetch_data
    def get(self):
        self.post()
        #self.redirect(calendar_prefix)

    # POST /fetch_data
    def post(self):
        """Fetches the user's data."""

        feed_url = constants.Constants.CAL_FEED_ALL_CALENDARS;
        #feed_url = 'https://www.google.com/calendar/feeds/default/owncalendars/full/'
        #feed_url = 'https://www.google.com/calendar/feeds/15k5jcgdnscdj9j5lposl32hms%40group.calendar.google.com/private/full'
        try:
            json = [];

            response = gcal.Get(feed_url)
            # for xml
            #response = gcal.Get(feed_url, converter=str)            
            #self.response.out.write(response)
            if isinstance(response, atom.Feed):
                for entry in response.entry:
                    json.append({'title': entry.title.text,
                                 'id': entry.id.text,
                                 'published': entry.published.text,
                                 'updated': entry.updated.text,
                                 })
            #    json = [{"state":"Feed Format"}];
            elif isinstance(response, atom.Entry):
                json.append({'title': response.title.text})
            #    json = [{"state":"Entry Format"}];
            else:
                json = [{"state": "Unknown Format"}];

                #feed = gcal.GetCalendarListFeed()

                #for entry in feed.entry:
                #json.append({'title': entry.title.text,
                #    })
            self.response.out.write(simplejson.dumps(json))
        except gdata.service.RequestError, error:
            json = [{"state": error}];
            self.response.out.write(simplejson.dumps(json))
            pass


class CurrencyConverter(webapp2.RequestHandler):
    # GET /currency_converter
    def get(self):
        self.post()
        #self.redirect(calendar_prefix)

    # POST /currency_converter
    def post(self):
        amount = self.request.get('amount', default_value=1);
        fromCur = self.request.get('fromCur', default_value=constants.Constants.CAL_FROM_CUR);
        toCur = self.request.get('toCur', default_value=constants.Constants.CAL_TO_CUR);

        convertURL = constants.Constants.CURRENCY_URL + '?hl=en&q=' + str(amount) + fromCur\
                     + '=?' + toCur;
        response = urlfetch.fetch(convertURL)
        regexp1 = re.compile(r"[\w,.:]")
        result = regexp1.findall(response.content);

        if response.status_code == 200:
            self.response.out.write("".join(result));
        else:
            self.response.out.write(400);


class RevokeToken(webapp2.RequestHandler):
    # GET /revoke_token
    def get(self):
        """Revokes the current user's OAuth access token."""

        try:
            gcal.RevokeOAuthToken()
        except gdata.service.RevokingOAuthTokenFailed:
            pass

        gcal.token_store.remove_all_tokens()
        self.redirect(calendar_prefix)


class ErrorPage(webapp2.RequestHandler):
    def get(self):
        template_dict = {
            "error_source": "Calendar"};
        self.response.out.write(django_loader.render_to_string("404.html", template_dict));

app = webapp2.WSGIApplication([(calendar_prefix, MainPage),
    (calendar_prefix + '/get_oauth_token', OAuthDance),
    (calendar_prefix + '/fetch_data', FetchData),
    (calendar_prefix + '/fetch_calendar', FetchCalendar),
    (calendar_prefix + '/revoke_token', RevokeToken),
    (calendar_prefix + '/currency_converter', CurrencyConverter),
    (calendar_prefix + '.*', ErrorPage)],
    debug=True)

