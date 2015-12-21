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
import bottle
import os
import pymongo
import cgi
import logging
import userDAO
import roomDAO
import sessionDAO
import groupDAO
import utils


APP_ROOT = os.path.dirname(__file__)
# locale.setlocale(locale.LC_TIME, 'it_IT.utf8')

# Logging
LOG_DIR = 'logs'
LOG_FILE = 'roomer-app.log'
LOG_PATH = os.path.join(APP_ROOT, LOG_DIR, LOG_FILE)

# create file if it doesn't exist
if not os.path.exists(LOG_PATH):
    f = open(LOG_PATH, 'w')
    f.close()
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename=LOG_PATH,
                    level=logging.INFO)
logging.info('Started.')
# End Logging

app = bottle.Bottle()
bottle.TEMPLATE_PATH.insert(0, os.path.join(APP_ROOT, 'views'))


# Static files
@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return bottle.static_file(filename,
                              root=os.path.join(APP_ROOT, 'static/js'))


@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return bottle.static_file(filename,
                              root=os.path.join(APP_ROOT, 'static/css'))


@app.get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return bottle.static_file(filename,
                              root=os.path.join(APP_ROOT, 'static/css/images'))


@app.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return bottle.static_file(filename,
                              root=os.path.join(APP_ROOT, 'static/fonts'))


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
        # TO DO: gestire gruppi multipli (w.a. creare gruppo che vede tutto)
        group_rooms = groups.get(user_data['groups'][0])['rooms']
        raw_rooms_data = rooms.get_rooms(group_rooms)
        user_reservations = rooms.get_reservations_by_user(username)
        reservations = []
        for res in user_reservations:
            res['reservations']['day'] = utils.get_reservation_day(res)
            res['reservations']['start'] = utils.get_reservation_start(res)
            res['reservations']['end'] = utils.get_reservation_end(res)
            reservations.append(res)
        for room in raw_rooms_data:
            rooms_data.append(utils.format_room_data(room))
        logging.info("Welcome: %s", username)
        return bottle.template('home',
                               dict(user=user_data,
                                    rooms=rooms_data,
                                    reservations=reservations))


# displays the initial app login form
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
        user_data = users.get_user(username)
        group_rooms = groups.get(user_data['groups'][0])['rooms']
        if str(rooms.get_room_id(name)) in group_rooms:
            room_data = utils.format_room_data(rooms.get_room(name))
            rooms_names = rooms.get_rooms(group_rooms)
            return bottle.template('room', dict(user=user_data,
                                                room_data=room_data,
                                                rooms_names=rooms_names))
        else:
            bottle.redirect("/login")


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
    from bottle import request
    start = int(request.query.start)
    end = int(request.query.end)
    return rooms.get_events(name,
                            utils.epoch_to_iso(start),
                            utils.epoch_to_iso(end))

@app.get('/users_list')
def display_users():
    # user_ids = users.get_user_ids()
    # print(user_ids)
    # username = bottle.request.forms.get("username")
    # return bottle.template('users', users=user_ids, rooms=None)
    return bottle.template('users', rooms=None)


@app.get('/users')
def get_users():
    import json
    return json.dumps({'data': users.get_user_ids()})

@app.post('/insert_event')
def insert():
    items = list(bottle.request.forms.items())
    event = utils.to_dict(items)
    logging.info("Preparing to inserting event %s", event)
    # Compute data to manage recursive events
    options = {"never": 0, "day": 1, "week": 7}
    delta = options[event['repeat']]
    if delta == 0:
        # non recurring event
        n_events = 1
        event['until'] = 0
    else:
        # recurring event, check for overlapping
        event['until'] = utils.str_to_date(event['until'])
        if utils.is_overlapping(bottle.request, rooms):
            logging.info("Event not inserted due to overlapping conditions.")
            return False
        else:
            n_events = ((event['until'] -
                         event['start']).days / delta
                        + event['num'] + 1)

    # Generate event(s)
    events = []
    for count in range(int(n_events)):
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
    items = list(bottle.request.forms.items())
    event = utils.to_dict(items)
    if event['scope'] == 'all':
        event['num'] = None
    logging.info("Updating event %s", event)
    rooms.update_event(event['room'], event)


@app.post('/remove_event')
def remove_event():

    items = list(bottle.request.forms.items())
    event = utils.to_dict(items)
    if event['scope'] == "onlyThis":
        logging.info("Removing only occurence number %s from event %s",
                     event['num'], event)
        rooms.remove_event(event['room'], event['id'], event['num'])
    else:
        logging.info("Removing all occurences of event %s", event)
        rooms.remove_event_from_here(event['room'], event['id'], 0)


def get_session_username():
    cookie = bottle.request.get_cookie("session")
    return sessions.get_username(cookie)


if 'MONGOHQ_URL' in os.environ:
    connection_string = os.environ['MONGOHQ_URL']
    connection = pymongo.MongoClient(connection_string)
    database = connection.get_default_database.__func__(connection)
else:
    connection_string = "mongodb://localhost"
    connection = pymongo.MongoClient(connection_string)
    database = connection.roomer

users = userDAO.UserDAO(database)
rooms = roomDAO.RoomDAO(database)
sessions = sessionDAO.SessionDAO(database)
groups = groupDAO.groupDAO(database)
port = os.environ.get('PORT', '8090')

if os.name == 'nt':
    pass
else:
    app.run(host='0.0.0.0', port=port, debug=True,
            reloader=True, server='cherrypy')
