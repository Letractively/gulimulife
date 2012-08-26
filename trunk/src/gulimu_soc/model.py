__author__ = 'xlzhu'

from google.appengine.ext import db

class Tag(db.Model):
  user_ = db.UserProperty(required=True)
  name_ = db.StringProperty(required=True)

class Language(Tag):
  color_ = db.StringProperty(required=True)

class Entry(db.Model):
  title_ = db.StringProperty(required=True)
  user_ = db.UserProperty(required=True)
  date_ = db.DateProperty(required=True)
  language_list_ = db.ListProperty(db.Key)
  tag_list_ = db.ListProperty(db.Key)
