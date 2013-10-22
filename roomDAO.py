import datetime
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

    def insert_event(self, room, events):

        self.db.rooms.update({"name": room}, {"$push": {"reservations": {"$each": events}}})

    def read_event(self, room):
        
        query = {"name": room}
        projection = {"reservations": 1, "_id": 0}

        events = self.db.rooms.find_one(query, projection)
        for event in events['reservations']:
            event['start'] = event['start'].isoformat()
            event['end'] = event['end'].isoformat()
            if type(event['until']) == int:
                pass
            else:
                event['until'] = event['until'].isoformat()
        return json.dumps(events["reservations"], default=json_util.default)
        #return events["reservations"]

    def update_event(self, room, event):

        query = { "name": room, "reservations.id": event["id"]}
        event = { "$set": { "reservations.$.title" : event["title"],
                            "reservations.$.start" : event["start"],
                            "reservations.$.end" : event["end"],
                            "reservations.$.allDay" : event["allDay"],
                            "reservations.$.until": event["until"] } 
                        }
        self.db.rooms.update( query, event)

    def remove_event(self, room, id):
        self.db.rooms.update({"name": room}, {"$pull": {"reservations": {"id": id}}})


    def get_rooms(self):

        rooms = []

        try:
            cursor = self.rooms.find(fields={'_id': False, 'reservations': False})
        except:
            print "Unable to query database for user"
        
        for doc in cursor:
            rooms.append(doc)
            
        return rooms
        
    def check_overlapping(self, id, start, start_hour, start_min, end_hour, end_min, until):
        
        try:
            cursor = self.rooms.aggregate(
                [
                    {
                        "$unwind": "$reservations"
                    },
                    {
                        "$match":
                        {
                            "reservations.end": {"$lte": until},
                            "reservations.start": {"$gte": start}
                        }
                    },
                    {
                        "$project":
                        {
                            "_id": "$reservations.id",
                            "day":{"$dayOfYear": "$reservations.start"},
                            "s_hour": {"$hour": "$reservations.start"}, 
                            "s_minutes": {"$minute": "$reservations.start"}, 
                            "e_hour": {"$hour": "$reservations.end" }, 
                            "e_minutes": {"$minute": "$reservations.end"}
                        }
                    },
                    {
                        "$project": 
                        {
                            "day": 1, 
                            "sec_s": {"$add": [{"$multiply": ["$s_hour", 3600]}, {"$multiply": ["$s_minutes", 60]}]},
                            "sec_e": {"$add": [{"$multiply": ["$e_hour", 3600]}, {"$multiply": ["$e_minutes", 60]}]}
                        }
                    },
                    {
                        "$match": 
                        {
                            "_id": {"$ne": id},
                            "sec_s": {"$lt": end_hour*3600 + end_min*60},
                            "sec_e": {"$gt": start_hour*3600 + end_hour*60}
                        }
                    },
                    {
                        "$group": 
                        {"_id": "$day","count": {"$sum": 1}}
                    }
                ]
            )
        except:
            print "Unable to query database for user"    
        
        return cursor['result']
