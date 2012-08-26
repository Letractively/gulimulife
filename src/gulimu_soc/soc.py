__author__ = 'xlzhu'

g_prefix = '/soc'

# django settings
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# gae routines
import webapp2
import json
from django.template import loader as django_loader
from google.appengine.api import users
import datetime
import logging

#my own import
import model


class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri));

    eresult = model.Entry.gql("WHERE user_ = :1", user)
    tresult = model.Tag.all()
    lresult = model.Language.all()

    elist = []
    for ii in eresult:
      elist.append({
        'key': ii.key(),
        'user': ii.user_.nickname(),
        'title': ii.title_,
        'date': ii.date_,
        'tags': ii.tag_list_,
        'lang': ii.language_list_
      })

    tlist = []
    for ii in tresult:
      tlist.append({
        'key': ii.key(),
        'user': ii.user_.nickname(),
        'name': ii.name_
      })

    llist = []
    for ii in lresult:
      llist.append({
        'key': ii.key(),
        'user': ii.user_.nickname(),
        'name': ii.name_,
        'color': ii.color_
      })

    template_values = {
      'user': users.get_current_user(),
      'entry_list': elist,
      'language_list': llist,
      'tag_list': tlist
    }

    self.response.out.write(django_loader.render_to_string('sundayofcode/sundayofcode.html', template_values));


class GetAllEntries(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    result = model.Entry.gql("WHERE user_ = :1", user).get()

    resbody = json.encode(result)
    self.response.out.write(resbody)


class UpdateEntry(webapp2.RequestHandler):
  def update_tags(self, tags):
    user = users.get_current_user()
    keys = []
    if user:
      for ii in tags:
        ins = model.Tag.gql("WHERE name_=:1 AND user_=:2", ii, user).get()
        if ins is None:
          ins = model.Tag(
            user_=user,
            name_=l_name
          )
          ins.put()
          keys.append(ins.key())
        else:
          keys.append(ins.key())
    return keys

  def update_languages(self, languages):
    user = users.get_current_user()
    keys = []
    if user:
      for ii in languages:
        ins = model.Language.gql("WHERE name_=:1 AND user_=:2", ii, user).get()
        if ins is None:
          ins = model.Language(
            user_=user,
            name_=l_name,
            color_='#CCC'
          )
          ins.put()
          keys.append(ins.key())
        else:
          keys.append(ins.key())
    return keys

  def post(self):
    user = users.get_current_user()

    if not user:
      self.response.status_id = 500
    else:
      logging.info(self.request.body)
      data = json.loads(self.request.body)
      logging.info(data)

      l_date_str = data['date']
      l_title = data['title']
      l_tags = data['tags']
      l_languages = data['lang']
      l_date = datetime.datetime.strptime(l_date_str, "%m/%d/%Y").date()

      logging.info(l_title)
      logging.info(l_date)
      logging.info(l_tags)
      logging.info(l_languages)

      ins = model.Entry.gql("WHERE user_ = :1 AND date_ = :2", user, l_date).get()

      if ins is None:
        tkeys = self.update_tags(l_tags)
        lkeys = self.update_languages(l_languages)
        ins = model.Entry(
          title_=l_title,
          user_=user,
          date_=l_date
        )
        for ii in tkeys:
          ins.tag_list_.append(ii)
        for ii in lkeys:
          ins.language_list_.append(ii)
        ins.put()
      else:
        tkeys = self.update_tags(l_tags)
        lkeys = self.update_languages(l_languages)
        ins.title_ = l_title

        ts = ins.tag_list_
        for ii in tkeys:
          if ii not in ts:
            ts.append(ii)
        ls = ins.language_list_
        for ii in lkeys:
          if ii not in ls:
            ls.append(ii)
        ins.put()

      self.response.out.write("yoyoyo")




class UpdateTag(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()

    if not user:
      self.response.status_id = 500
    else:
      l_name = self.request.get('name')

      ins = model.Tag.gql("WHERE name_=:1 AND user_=:2", l_name, user).get()

      if ins is None:
        ins = model.Tag(
          user_=user,
          name_=l_name
        )
        ins.put()

      self.response.out.write("yoyoyo")


class UpdateLanguage(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()

    if not user:
      self.response.status_id = 500
    else:
      l_name = self.request.get('name')
      l_color = self.request.get('color', '#ccc')

      ins = model.Language.gql("WHERE name_=:1 and user_=:2", l_name, user).get()

      logging.info(l_name)
      logging.info(l_color)

      if ins is None:
        ins = model.Language(
          user_=user,
          name_=l_name,
          color_=l_color
        )
        ins.put()
      else:
        ins.color_ = l_color
        ins.put()

app = webapp2.WSGIApplication([(g_prefix, MainPage),
  (g_prefix + '/get_entries', GetAllEntries),
  (g_prefix + '/update_entry', UpdateEntry),
  (g_prefix + '/update_tag', UpdateTag),
  (g_prefix + '/update_language', UpdateLanguage)],
  debug=True)
