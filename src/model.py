'''
Created on 26 Sep 2010

@author: gulimujyujyu
'''

from google.appengine.ext import db

class Place(db.Model):
    name = db.StringProperty(required=True)
    ll = db.GeoPtProperty

class Object(db.Model):
    name = db.StringProperty(required=True)
    type = db.IntegerProperty(required=True)
    email = db.EmailProperty()
    address = db.ReferenceProperty()
    url = db.URLProperty()
    
class Event(db.Model):
    source = db.ReferenceProperty(Object) 
    place = db.ReferenceProperty(Place)
    time = db.DateTimeProperty(required=True)
    imageUrl = db.URLProperty();
    content = db.StringProperty();
