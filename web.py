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

import bottle
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
        room_names = rooms.get_room_names()
        return bottle.template('home', dict(username=username,
                                            rooms=room_names['names']))

# displays the initial blog login form
@bottle.get('/login')
def present_login():

    username = get_session_username()

    if username is None:
        return bottle.template("login",
                                dict(username="", login_error=""))
    else:
        bottle.redirect("/")

@bottle.post('/login')
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
    bottle.redirect("/login")

@bottle.get('/room/<name>')
def get_room(name):

    username = get_session_username()  # see if user is logged in
    
    if username is None:
        bottle.redirect("/login")
    else:
        room = rooms.get_room(name)
        room_names = rooms.get_room_names()
        return bottle.template('room', dict(user=username,
                                            room=room,
                                            rooms=room_names['names']))
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
    return rooms.read_event(name)

@bottle.post('/insert_event')
def insert_event():

    room = bottle.request.forms.get("room")
    event = dict(id = bottle.request.forms.get("id"),
                 title = bottle.request.forms.get("title"),                                                     
                 user = bottle.request.forms.get("user"),
                 start = bottle.request.forms.get("start"),
                 end = bottle.request.forms.get("end"),
                 allDay = eval(string.capitalize(bottle.request.forms.get("allDay"))))
    
    rooms.insert_event(room, event)

@bottle.post('/update_event')
def insert_event():

    # TODO: migliorare, e' uguale all'insert!!!

    room = bottle.request.forms.get("room")
    event = dict(id = bottle.request.forms.get("id"),
                 title = bottle.request.forms.get("title"),                                                     
                 user = bottle.request.forms.get("user"),
                 start = bottle.request.forms.get("start"),
                 end = bottle.request.forms.get("end"),
                 allDay = eval(string.capitalize(bottle.request.forms.get("allDay"))))
    
    rooms.update_event(room, event)

@bottle.post('/remove_event')
def remove_event():

    room = bottle.request.forms.get("room")
    id = bottle.request.forms.get("id")
    rooms.remove_event(room, id)


# Helper Functions  

def get_session_username():

    cookie = bottle.request.get_cookie("session")
    return sessions.get_username(cookie)



connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.roomer

users = userDAO.UserDAO(database)
rooms = roomDAO.RoomDAO(database)
sessions = sessionDAO.SessionDAO(database)

bottle.debug(True)
bottle.run(host='localhost', port=8080, reloader=True) 
