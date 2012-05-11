__author__ = 'xlzhu'

g_prefix = '/soc'

# django settings
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# gae routines
import webapp2
from django.template import loader as django_loader
from google.appengine.api import users

class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri));

    template_values = {
      'user': users.get_current_user(),
    }

    self.response.out.write(django_loader.render_to_string('sundayofcode/sundayofcode.html',template_values));


app = webapp2.WSGIApplication([(g_prefix, MainPage)],
    debug=True)
