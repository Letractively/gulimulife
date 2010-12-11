'''
Created on 12 Oct 2010

@author: gulimujyujyu
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template

import constants
import os

class MainPage(webapp.RequestHandler):
    
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
        
def main():
    url_map = [('/.*', MainPage), ]
             
    application = webapp.WSGIApplication(url_map, debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

