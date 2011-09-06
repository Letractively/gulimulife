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

from utils import constants

##Globals
everyday_prefix = '/everyday'

#main page
class MainPage(webapp.RequestHandler):
    title = 'Main Page'

    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri));

        template_values = {
            'user': users.get_current_user(),
        }

        #logging.info( constants.Constants.TEMPLATE_PATH)
        path = os.path.join(constants.Constants.TEMPLATE_PATH, 'everyday/everyday.html')
        self.response.out.write(template.render(path, template_values));

    def post(self):
        self.get();

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
