import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template

from utils import constants
import os

class MainPage(webapp2.RequestHandler):
    
    def get(self):

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'user_url': url,
            'url_linktext': url_linktext,
            }

        path = os.path.join(constants.Constants.TEMPLATE_PATH, 'index.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/.*', MainPage), ], debug=True)




