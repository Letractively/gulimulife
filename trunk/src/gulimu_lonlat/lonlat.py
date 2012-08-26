__author__ = 'xlzhu'

import os
import webapp2
from google.appengine.api import users
from django.template import loader as django_loader

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
url_prefix = '/lonlat'

class MainPage(webapp2.RequestHandler):
  def get(self):
    if not users.get_current_user():
      self.redirect(users.create_login_url(self.request.uri))

    template_values = {
      'user': users.get_current_user(),
    }

    self.response.out.write(django_loader.render_to_string('lonlat/lonlat.html', template_values))

class ErrorPage(webapp2.RequestHandler):
  def get(self):
    template_dict = {
      "error_source": "TravelMap"
    };
    self.response.out.write(django_loader.render_to_string('404.html', template_dict));

app = webapp2.WSGIApplication([(url_prefix, MainPage),
                                (url_prefix + '/*', ErrorPage)],
                                debug=True)