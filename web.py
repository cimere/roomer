#
# Copyright (c) 2008 - 2013 10gen, Inc. <http://10gen.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import time
import bottle
import os
import pymongo
import cgi
import string
import logging
import userDAO
import roomDAO
import sessionDAO
import locale

APP_ROOT = os.path.dirname(__file__)
# locale.setlocale(locale.LC_TIME, 'it_IT.utf8')
 
# Logging 
LOG_DIR = 'logs'
LOG_FILE = 'roomer-app.log'
LOG_PATH = os.path.join(APP_ROOT, LOG_DIR, LOG_FILE)

# create file if it doesn't exist
if not os.path.exists(LOG_PATH):
    f = file(LOG_PATH, 'w')
    f.close()
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename=LOG_PATH,
                    level=logging.INFO)
logging.info('Started.')
# End Logging

app = bottle.Bottle()
bottle.TEMPLATE_PATH.insert(0,os.path.join(APP_ROOT, 'views'))
         
# Static files
@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename, root=os.path.join(APP_ROOT, 'static/js'))

@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return bottle.static_file(filename, root=os.path.join(APP_ROOT, 'static/css'))

@app.get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename, root=os.path.join(APP_ROOT, 'static/css/images'))

@app.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return bottle.static_file(filename, root=os.path.join(APP_ROOT, 'static/fonts'))

# Route definitions

@app.route('/')
def home():

    username = get_session_username()

    if username is None:
        logging.info("Welcome: can't identify user...redirecting to signup")
        bottle.redirect("/login")
    else:
        rooms_data = []
        user_data = users.get_user(username)
        raw_rooms_data = rooms.get_rooms()
#        free_slots = get_free_slot(1)
        user_reservations = rooms.get_reservations_by_user(username)
        reservations = []
        for res in user_reservations:
            res['reservations']['day'] = res['reservations']['start'].strftime("%A %d")
            res['reservations']['start'] = res['reservations']['start'].strftime("%H:%M")
            res['reservations']['end'] = res['reservations']['end'].strftime("%H:%M")
            reservations.append(res)
        for room in raw_rooms_data:
            rooms_data.append(format_room_data(room))
        logging.info("Welcome: %s", username)
        return bottle.template('home',
                               dict(user = user_data,
                                    rooms=rooms_data,
                                    reservations=reservations))

# displays the initial blog login form
@app.get('/login')
def present_login():

    username = get_session_username()

    if username is None:
        # return bottle.template("login",
        #                        dict(username="", login_error=""))
        bottle.redirect("http://roomer")
    else:
        bottle.redirect("/")

@app.get('/test')
def present_test_login():

    print('sono qui')
    username = get_session_username()

    if username is None:
        return bottle.template("test",
                               dict(username="", login_error=""))
    else:
        bottle.redirect("/")

@app.post('/test')
@app.post('/login')
def process_login():
    
    username = bottle.request.forms.get("username")
    logging.info("Test user submitted: %s", username)

    user_record = users.validate_login(username)
    if user_record:
        # username is stored in the user collection in the _id key
        session_id = sessions.start_session(user_record['_id'])

        if session_id is None:
            bottle.redirect("/internal_error")

        cookie = session_id

        # Warning, if you are running into a problem whereby the cookie being set here is
        # not getting set on the redirect, you are probably using the experimental version of bottle (.12).
        # revert to .11 to solve the problem.
        bottle.response.set_cookie("session", cookie)

        bottle.redirect("/")

    else:
        return bottle.template("login",
                               dict(username=cgi.escape(username),
                                    login_error="Utente non valido."))

@app.get('/logout')
def process_logout():

    cookie = bottle.request.get_cookie("session")
    sessions.end_session(cookie)
    bottle.response.set_cookie("session", "")
    bottle.redirect("login")

@app.get('/room/<name>')
def get_room(name):

    username = get_session_username()  # see if user is logged in
    
    if username is None:
        logging.info("Can't identify user...redirecting to signup")
        bottle.redirect("/login")
    else:
        room_data = format_room_data(rooms.get_room(name))
        user_data = users.get_user(username)
        rooms_names = rooms.get_rooms()
        return bottle.template('room', dict(user=user_data,
                                room_data=room_data,
                                rooms_names=rooms_names))

@app.get('/user/<id>')
def get_user(id):

    user = users.get_user(id)
    return bottle.template('user', user=user)

@app.get('/get_user_ids')
def get_user_ids():
    # TODO: serve realmente?
    return users.get_user_ids()

@app.get('/get_events/<name>')
def get_events(name):

    return rooms.get_event(name)

@app.post('/insert_event')
def insert():
    items = bottle.request.forms.items()
    event = to_dict(items)
    logging.info("Preparing to inserting event %s", event)
    # Compute data to manage recursive events
    options = { "never": 0, "day": 1, "week": 7 }
    delta = options[event['repeat']]
    if delta == 0:
        # non recurring event
        n_events = 1
        event['until'] = 0
    else:
        # recurring event, check for overlapping
        event['until'] =  str_to_date(event['until'])
        if is_overlapping():
            logging.info("Event not inserted due to overlapping conditions.")
            return False
        else:
            n_events = (event['until'] - event['start']).days / delta + event['num'] +1  # count the first event too.
    
    # Generate event(s)
    events = []
    for count in range(n_events):
        events.append(event.copy())
        event['start'] += datetime.timedelta(delta)
        event['end'] += datetime.timedelta(delta)
        event['num'] += 1
    rooms.insert_event(event['room'], events)
    logging.info("Event corretly inserted.")
    return "true"

@app.post('/update_event')
def update_event():
    ''' Only title update for recursive event
    datetime update for single events'''
    items = bottle.request.forms.items()
    event = to_dict(items)
    if event['scope'] == 'all':
        event['num'] = None
    logging.info("Updating event %s", event)
    rooms.update_event(event['room'], event)

@app.post('/remove_event')
def remove_event():

    items = bottle.request.forms.items()
    event = to_dict(items)
    if event['scope'] == "onlyThis":
        logging.info("Removing only occurence number %s from event %s", event['num'], event)
        rooms.remove_event(event['room'], event['id'], event['num'])
    else:
        logging.info("Removing all occurences of event %s",event)
        rooms.remove_event_from_here(event['room'], event['id'], 0)

# Helper Functions  

def get_session_username():

    cookie = bottle.request.get_cookie("session")
    return sessions.get_username(cookie)

def ISO_str_to_date(string):

#    struct = time.strptime(string, "%a %b %d %Y %H:%M:%S GMT+0200 (CEST)")
#    unix = time.mktime(struct)
    date = datetime.datetime.fromtimestamp(int(string))
    return date

def str_to_date(string):

    struct = time.strptime(string, "%Y-%m-%dT%H:%M:%S")
    unix = time.mktime(struct)
    date = datetime.datetime.fromtimestamp(unix)
    return date

def day_to_date(day_number):
    ''' 
    Takes an integer input (e.g. 4) and returns a date (e.g. 1/4/2013)
    2013 = current year
    http://answers.yahoo.com/question/index?qid=20100805222947AAqMKfh
    '''
    first_of_year = datetime.datetime(time.localtime().tm_year, 1, 1)
    first_ordinal = first_of_year.toordinal()
    day_ordinal = first_ordinal - 1 + day_number
    return datetime.date.fromordinal(day_ordinal) 

def to_dict(items):
    ''' put a bottle.request.forms dict in a standard python dict
    and do some data type cast to store data in  mongoDB '''
    d = {}
    for key, value in items:
        d[key] = value
    d_keys = d.keys()
    if 'start' in d.keys():
        d['start'] = ISO_str_to_date(d['start'])
    if 'end' in d.keys():
        d['end'] =  ISO_str_to_date(d['end'])
    if 'num' in d.keys():
        d['num'] = int(d['num'])
    if 'allDay' in d.keys():
        d['allDay'] = eval(string.capitalize(d['allDay']))
    return d

def format_room_data(data):
    ''' list of dict --> list of dict
        in dict: {'tel', 'name', 'people', 'whiteboard', 'vdc', 'type': 'desc'}
        out dict: {'name', 'desc'}
    '''
    output = []
    desc = "Fino a "+str(data['people'])+" persone, "+data['whiteboard']+"."
    if data['tel'] is not None:
        desc += "Interno: "+str(data['tel'])+"."
    if data['vdc'] is not None:
        desc += "VDC: "+data['vdc']+". "
    return {"name": data["name"], "desc": desc}


def is_overlapping():

    id = bottle.request.forms.get("id")
    room = bottle.request.forms.get("room")
    repeat = bottle.request.forms.get("repeat")
    start = ISO_str_to_date(bottle.request.forms.get("start"))
    end =  ISO_str_to_date(bottle.request.forms.get("end"))
    if repeat != "never":
        # recurring event, check for overlapping
        until =  str_to_date(bottle.request.forms.get("until")) 
        if repeat == "week":
            week_day = start.isoweekday() + 1 # on mongodb week start on Sunday
        else:
            week_day = None

        overlapping = rooms.check_overlapping(room, id, start,
                                              start.hour, start.minute,
                                              end.hour, end.minute,
                                              until, week_day)
        if overlapping == []:
            # not overlapping
            logging.info("No overlapping events found.")
            return False
        else:
            overlapping_events = []
            for event in overlapping:
                overlapping_events.append(day_to_date(event['day']).isoformat())
            logging.info("Overlapping events: %s", repr(overlapping_events))
            return True            

def get_free_slot(duration):
    print(rooms.get_free_slots(duration))

if 'MONGOHQ_URL' in os.environ:
    connection_string = os.environ['MONGOHQ_URL']
    connection = pymongo.MongoClient(connection_string)
    database = connection.get_default_database.im_func(connection)
else:
    connection_string = "mongodb://localhost"
    connection = pymongo.MongoClient(connection_string)
    database = connection.roomer

users = userDAO.UserDAO(database)
rooms = roomDAO.RoomDAO(database)
sessions = sessionDAO.SessionDAO(database)
    
port = os.environ.get('PORT', '8080')

bottle.run(app, host='0.0.0.0', port=port, debug=True, reloader=True, server='cherrypy')
