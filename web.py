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
#

import datetime
import time
import bottle
import os
import pymongo
import cgi
import userDAO
import roomDAO
import sessionDAO
import string

# TODO ADD session management (done)

# Static files

# @bottle.get('/static/<filepath:path>')
# def server_static(filepath):

#     root_url = '/home/mere/Dropbox/me/programming/roomer/static'
#     return bottle.static_file(filepath, root=root_url)

@bottle.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename, root='static/js')

@bottle.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return bottle.static_file(filename, root='static/css')

@bottle.get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename, root='static/css/images')

@bottle.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return bottle.static_file(filename, root='static/fonts')

# Route definitions

@bottle.route('/')
def home():

    username = get_session_username()

    if username is None:
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/login")
    else:
        user_data = users.get_user(username)
        rooms_data = rooms.get_rooms()
        return bottle.template('home', dict(user = user_data,
                                            rooms=rooms_data))

# displays the initial blog login form
@bottle.get('/login')
def present_login():

    username = get_session_username()

    if username is None:
        return bottle.template("login",
                               dict(username="", login_error=""))
    else:
        bottle.redirect("/")

@bottle.get('/test')
def present_test_login():

    username = get_session_username()

    if username is None:
        return bottle.template("test",
                               dict(username="", login_error=""))
    else:
        bottle.redirect("/")

@bottle.post('/test')
def process_login():
    
    username = bottle.request.forms.get("username")
    print "user submitted ", username

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

@bottle.get('/logout')
def process_logout():

    cookie = bottle.request.get_cookie("session")
    sessions.end_session(cookie)
    bottle.response.set_cookie("session", "")
    bottle.redirect("login")
    # enable in prod:
    #bottle.redirect("/roomer")

@bottle.get('/room/<name>')
def get_room(name):

    username = get_session_username()  # see if user is logged in
    
    if username is None:
        bottle.redirect("/login")
    else:
        room_data = rooms.get_room(name)
        user_data = users.get_user(username)
        rooms_names = rooms.get_rooms()
        return bottle.template('room', dict(user=user_data,
                                            room_data=room_data,
                                            rooms_names=rooms_names))

@bottle.get('/user/<id>')
def get_user(id):

    user = users.get_user(id)
    return bottle.template('user', user=user)

@bottle.get('/get_user_ids')
def get_user_ids():
    # TODO: serve realmente?
    return users.get_user_ids()

@bottle.get('/get_events/<name>')
def get_events(name):

    return rooms.get_event(name)

@bottle.post('/insert_event')
def insert_event():

    events = []

    id = bottle.request.forms.get("id")
    title = bottle.request.forms.get("title")
    user = bottle.request.forms.get("user")
    room = bottle.request.forms.get("room")
    repeat = bottle.request.forms.get("repeat")
    until = bottle.request.forms.get("until")
    start = ISO_str_to_date(bottle.request.forms.get("start"))
    end =  ISO_str_to_date(bottle.request.forms.get("end"))
    allDay = eval(string.capitalize(bottle.request.forms.get("allDay")))
    repeat = bottle.request.forms.get("repeat")
    start_event = bottle.request.forms.get("startEvent")
    num = int(bottle.request.forms.get("num")) # if insert POST, num = 0 
    # Compute data to manage recursive events
    options = {"never": 0, # never repeat
               "day": 1, 
               "week": 7
    }
    delta = options[repeat]
    if delta == 0:
        # non recurring event
        n_events = 1
        until = 0
    else:
        # recurring event, check for overlapping
        until =  str_to_date(until)
        if is_overlapping():
            return False
        else:
            # not overlapping
            if start_event == 'fromHere':
                n_events = (until - start).days / delta + 1 # count the first event too.
            elif start_event == 'onlyThis':
                n_events = 1
            else: #fromStart
                n_events = (until - start).days / delta + 1 + num # count the first event too.
                start = start - datetime.timedelta(days=num)
                end = end - datetime.timedelta(days=num)

        
    # Generate event(s)
    for count in range(n_events):
        event = dict(
            id = id,
            title = title,
            user = user,
            start = start,
            end = end,
            allDay = allDay,
            repeat = repeat,
            until = until,
            num = count
        )
        start += datetime.timedelta(delta)
        if allDay:
            pass
        else:
            end += datetime.timedelta(delta)
        events.append(event)
        
    rooms.insert_event(room, events)


@bottle.post('/update_event')
def update_event():
    if is_overlapping():
        return False
    remove_event()
    insert_event()
    repeat = bottle.request.forms.get("repeat")

@bottle.post('/remove_event')
def remove_event():

    room = bottle.request.forms.get("room")
    id = bottle.request.forms.get("id")
    repeat = bottle.request.forms.get("repeat")
    start_event = bottle.request.forms.get("startEvent")
    if repeat == "never":
        rooms.remove_event(room, id, 0)
    else:
        if start_event == "onlyThis":
            num = int(bottle.request.forms.get("num"))
            rooms.remove_event(room, id, num)
        elif start_event == "fromHere":
            num = int(bottle.request.forms.get("num"))
            rooms.remove_event_from_here(room, id, num)
        else: # fromStart
            rooms.remove_event_from_here(room, id, 0)

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


def is_overlapping():

    id = bottle.request.forms.get("id")
    room = bottle.request.forms.get("room")
    repeat = bottle.request.forms.get("repeat")
    start = ISO_str_to_date(bottle.request.forms.get("start"))
    end =  ISO_str_to_date(bottle.request.forms.get("end"))
    if repeat != "never":
        # recurring event, check for overlapping
        until =  str_to_date(bottle.request.forms.get("until")) 
        print room, start, start.hour, start.minute, end.hour, end.minute, until
        overlapping = rooms.check_overlapping(room, id, start,
                                              start.hour, start.minute,
                                              end.hour, end.minute,
                                              until)
        print overlapping
        if overlapping == []:
            # not overlapping
            return False
        else:
            return True


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
bottle.debug(True)
bottle.run(host='0.0.0.0', port=port, reloader=True) 
