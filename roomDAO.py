import pymongo
import json
from bson import json_util, ObjectId


# The User Data Access Object handles all interactions with the User collection.
class RoomDAO:

    def __init__(self, db):
        self.db = db
        self.rooms = self.db.rooms
        # self.SECRET = 'verysecret'

    def get_room(self, name):

        try:
            room = self.rooms.find_one({"name": name})
        except:
            print "Unable to query database for user"

        return room

    def insert_event(self, room, event):
        ''' update on room, use ObjectId to generate unique id!'''
        self.db.rooms.update({"name": room}, {"$push": {"reservations": event}})

    def read_event(self, room):
        
        query = {"name": room}
        projection = {"reservations": 1, "_id": 0}

        events = self.db.rooms.find_one(query, projection)
        return json.dumps(events["reservations"], default=json_util.default)
        #return events["reservations"]

    def update_event(self, room, event):

        query = { "name": room, "reservations.id": event["id"]}
        event = { "$set": { "reservations.$.title" : event["title"],
                          "reservations.$.start" : event["start"],
                          "reservations.$.end" : event["end"],
                          "reservations.$.allDay" : event["allDay"] } 
                        }
        self.db.rooms.update( query, event)

    def remove_event(self, room, id):
        print room, id
        self.db.rooms.update({"name": room}, {"$pull": {"reservations": {"id": id}}})


    def get_room_names(self):

        names = {'names': []}

        try:
            cursor = self.rooms.find()
        except:
            print "Unable to query database for user"

        for doc in cursor:
            names['names'].append(doc['name'])

        return names