'''
Created on 26 Sep 2010

@author: gulimujyujyu
'''
import os
from datetime import date
from datetime import timedelta

class Constants:
    TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'templates');
    
    CAL_MONEY_ID = '15k5jcgdnscdj9j5lposl32hms%40group.calendar.google.com';
    CAL_FEEDURL = 'https://www.google.com/calendar/feeds/'
    CAL_FEED_ALL_CALENDARS = 'https://www.google.com/calendar/feeds/default/allcalendars/full'
    CURRENCY_URL = 'http://www.google.com/ig/calculator'
    
    CAL_PROJECTION = '/private/full';
    CAL_TODAY = date.today();
    CAL_LASTM_FOUR_WEEKS = CAL_TODAY - timedelta(weeks=5);
    CAL_START = CAL_LASTM_FOUR_WEEKS.isoformat() + 'T00:00:00';
    CAL_FROM_CUR = 'RMB';
    CAL_TO_CUR = 'HKD';
    
    CAL_END = CAL_TODAY.isoformat() + 'T23:59:59';
    CAL_MAX_RESULTS = '500';
    
    #feed_url = 'https://www.google.com/calendar/feeds/15k5jcgdnscdj9j5lposl32hms%40group.calendar.google.com/private/full'
