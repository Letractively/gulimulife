'''
Created on 12 Oct 2010

@author: gulimujyujyu
'''
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template

import os
from utils import constants

class MainPage(webapp2.RequestHandler):
    
    def get(self):

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            }

        path = os.path.join(constants.Constants.TEMPLATE_PATH, '404.html')
        self.response.out.write(template.render(path, template_values))
             
app = webapp2.WSGIApplication([('/.*', MainPage), ], debug=True)


