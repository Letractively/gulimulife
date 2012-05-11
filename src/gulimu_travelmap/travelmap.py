'''
Created on 11 Oct 2010

@author: gulimujyujyu
'''
#!/usr/bin/python
#

import cgi
import re
import os

import json as simplejson
from google.appengine.api import users
import webapp2
from django.template import loader as django_loader

from google.appengine.ext import db

from utils import constants

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

#begin{Models}
class Trip(db.Model):
    author = db.UserProperty();
    name = db.StringProperty();
    geo = db.GeoPtProperty();
    #time = db.DateProperty();
    
class Information(db.Model):
    trip = db.ReferenceProperty(Trip);
    author = db.UserProperty();
    type = db.StringProperty();
    content = db.StringProperty();
    geo = db.GeoPtProperty();
    #rating = db.RatingProperty();
    
class Memo(db.Model):
    trip = db.ReferenceProperty(Trip);
    author = db.UserProperty();
    content = db.StringProperty();
    #rating = db.RatingProperty();
#end{Models}

travelmap_prefix = '/travelmap'

class MainPage(webapp2.RequestHandler):
    title = 'MainPage'

    # GET /
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))

        template_values = {
            'user': users.get_current_user(),
        }

        self.response.out.write(django_loader.render_to_string('travelmap/travelmap.html', template_values))
        
        

class FetchTrip(webapp2.RequestHandler):
    # GET
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        try:
            results = db.GqlQuery("SELECT * FROM Trip")
            
            json = [];
            for entry in results:
                if entry.geo:
                    json.append({'trip_key': entry.key().__str__(),
                             'author': entry.author.nickname(),
                             'name': entry.name,
                             'geo_lat': 22.49,
                             'geo_lon': 22.49,
                             #'time': entry.time,
                            })
                else:
                    json.append({'trip_key': entry.key().__str__(),
                             'author': entry.author.nickname(),
                             'name': entry.name,
                             'geo_lat': 22.49,
                             'geo_lon': 114,
                             #'time': entry.time,
                            })
            self.response.out.write(simplejson.dumps(json))
            
        except webapp.RequestHandler.error:
            self.response.out.write("[{state:error}]")
            pass

class FetchOneTrip(webapp2.RequestHandler):
    # GET
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        
        try:
            entry = Trip.get(trip);
            json = [];
            if entry.geo:
                json.append({'trip_key': entry.key().__str__(),
                         'author': entry.author.nickname(),
                         'name': entry.name,
                         'geo_lat': entry.geo.lat,
                         'geo_lon': entry.geo.lon,
                         #'time': entry.time,
                        })
            else:
                json.append({'trip_key': entry.key().__str__(),
                         'author': entry.author.nickname(),
                         'name': entry.name,
                         'geo_lat': 22.49,
                         'geo_lon': 114,
                         #'time': entry.time,
                        })
            self.response.out.write(simplejson.dumps(json))
            
        except webapp.RequestHandler.error:
            self.response.out.write("[{state:error}]")
            pass

class AddTrip(webapp2.RequestHandler):
    # GET
    def get(self):
        self.post();
        
    # POST
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        author = users.get_current_user();
        name = self.request.get('name');
        geo_lat = self.request.get('geo_lat');
        geo_lon = self.request.get('geo_lon');
        
        newTrip = Trip();
        newTrip.author = author;
        if geo_lat and geo_lon:
            geopt = db.GeoPt(lat=geo_lat, lon=geo_lon);
            newTrip.geo = geopt;
        else:
            geopt = db.GeoPt(lat=22.49, lon=114);
            newTrip.geo = geopt;
        newTrip.name = name;
        newTrip.put();
        
        json = [];
        json.append({'trip_key': newTrip.key().__str__(),
                     'author': newTrip.author.nickname(),
                     'name': newTrip.name,
                     'geo_lat': newTrip.geo.lat,
                     'geo_lon': newTrip.geo.lon,
                     #'time': entry.time,
                     })
        self.response.out.write(simplejson.dumps(json))
        #self.response.out.write("[{state:200}]")
        #time = self.request.get('time');

class FetchInformation(webapp2.RequestHandler):
    # GET
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        
        try:
            results = db.GqlQuery("SELECT * FROM Information WHERE trip = :tripObj", tripObj=trip)
            
            json = [];
            for entry in results:
                json.append({'information_key': entry.key().__str__(),
                             'trip_name': entry.trip.name,
                             'author': entry.author.nickname(),
                             'content': entry.content,
                             'geo_lat': entry.geo.lat,
                             'geo_lon': entry.geo.lon,
                             #'rating': entry.rating,
                            })
                
            self.response.out.write(simplejson.dumps(json))
                
        except webapp.RequestHandler.error:
            self.response.out.write("[{state:error}]")
            pass
        
class AddInformation(webapp2.RequestHandler):
    # GET
    def get(self):
        self.post();
        
    # POST
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        info_key = self.request.get('info');
        
        response_item = None;
        branch = 1;
        #
        if info_key:
            info_key_model = db.Key(info_key)
            info = Information.get(info_key_model);
            geo_lat = self.request.get('lat');
            geo_lon = self.request.get('lon');
            if geo_lat and geo_lon:
                geopt = db.GeoPt(lat=geo_lat, lon=geo_lon);
                info.geo = geopt;
            info.trip = trip;
            info.type = self.request.get('type') if self.request.get('type') else info.type;
            info.content = self.request.get('content') if self.request.get('content') else info.content;
            info.author = users.get_current_user();
            info.put();
            response_item = info;
        else:
            newInformation = Information();
            geo_lat = self.request.get('lat');
            geo_lon = self.request.get('lon');
            if geo_lat and geo_lon:
                geopt = db.GeoPt(lat=geo_lat, lon=geo_lon);
                newInformation.geo = geopt;
            newInformation.trip = trip;
            newInformation.type = self.request.get('type') if self.request.get('type') else newInformation.type;
            newInformation.content = self.request.get('content') if self.request.get('content') else newInformation.content;
            newInformation.author = users.get_current_user();
            newInformation.put();
            response_item = newInformation
            branch = 2;
            
        json = [];
        json.append({'information_key': response_item.key().__str__(),
                             'trip_name': response_item.trip.name,
                             'author': response_item.author.nickname(),
                             'content': response_item.content,
                             'geo_lat': response_item.geo.lat,
                             'geo_lon': response_item.geo.lon,
                             'branch': branch,
                             #'rating': entry.rating,
                            })
        self.response.out.write(simplejson.dumps(json))
        #time = self.request.get('time');

class AddInformationContent(webapp2.RequestHandler):
    def get(self):
        self.post();
        
    # POST
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        info_key = self.request.get('info');
        
        response_item = None;
        branch = 1;
        #
        if info_key:
            info_key_model = db.Key(info_key)
            info = Information.get(info_key_model);
            geo_lat = self.request.get('lat');
            geo_lon = self.request.get('lon');
            if geo_lat and geo_lon:
                geopt = db.GeoPt(lat=geo_lat, lon=geo_lon);
                info.geo = geopt;
            info.trip = trip;
            info.type = self.request.get('type') if self.request.get('type') else info.type;
            info.content = self.request.get('content') if self.request.get('content') else info.content;
            info.author = users.get_current_user();
            info.put();
            response_item = info;
        else:
            newInformation = Information();
            geo_lat = self.request.get('lat');
            geo_lon = self.request.get('lon');
            if geo_lat and geo_lon:
                geopt = db.GeoPt(lat=geo_lat, lon=geo_lon);
                newInformation.geo = geopt;
            newInformation.trip = trip;
            newInformation.type = self.request.get('type') if self.request.get('type') else newInformation.type;
            newInformation.content = self.request.get('content') if self.request.get('content') else newInformation.content;
            newInformation.author = users.get_current_user();
            newInformation.put();
            response_item = newInformation
            branch = 2;
        
        if response_item.content:
            self.response.out.write(response_item.content)
        else:
            self.response.out.write("No content")
        
        
class FetchMemo(webapp2.RequestHandler):
    # GET
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        
        try:
            results = db.GqlQuery("SELECT * FROM Memo WHERE trip = :tripObj", tripObj=trip)
            
            json = [];
            for entry in results:
                json.append({'memo_key': entry.key().__str__(),
                             'trip_name': entry.trip.name,
                             'author': entry.author.nickname(),
                             'content': entry.content,
                             #'geo': entry.geo,
                             #'rating': entry.rating,
                            })
                
            self.response.out.write(simplejson.dumps(json))
                
        except webapp.RequestHandler.error:
            self.response.out.write("[{state:error}]")
            pass
        
class AddMemo(webapp2.RequestHandler):
    # GET
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        newMemo = Memo();
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        newMemo.trip = trip;
        newMemo.content = self.request.get('content');
        newMemo.author = users.get_current_user();
        newMemo.put();
        
        self.response.out.write("[{state:200}]")
        
    # POST
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        
        newInformation = Information();
        trip_key = self.request.get('trip');
        trip = db.Key(trip_key);
        newInformation.trip = trip;
        newInformation.content = self.request.get('content');
        newInformation.author = users.get_current_user();
        newInformation.put();
        
        self.response.out.write("[{state:200}]")
        #time = self.request.get('time');
        
class ErrorPage(webapp2.RequestHandler):
    
    def get(self):
        template_dict = {
            "error_source": "TravelMap"};
        self.response.out.write(django_loader.render_to_string('404.html', template_dict));

app = webapp2.WSGIApplication([(travelmap_prefix, MainPage),
                                          (travelmap_prefix + '/fetch_trip', FetchTrip),
                                          (travelmap_prefix + '/fetch_trip_content', FetchOneTrip),
                                          (travelmap_prefix + '/add_trip', AddTrip),
                                          (travelmap_prefix + '/fetch_information', FetchInformation),
                                          (travelmap_prefix + '/add_information', AddInformation),
                                          (travelmap_prefix + '/add_information_content', AddInformationContent),
                                          (travelmap_prefix + '/fetch_memo', FetchMemo),
                                          (travelmap_prefix + '/add_memo', AddMemo),
                                          (travelmap_prefix + '.*', ErrorPage)],
                                         debug=True)
