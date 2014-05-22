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
        ''' Get room data, return one room document. '''
        try:
            room = self.rooms.find_one({"name": name})
        except:
            print "Unable to query database for user"

        return room

    def get_rooms(self):
        ''' Get data for all rooms. '''
        rooms = []

        try:
            cursor = self.rooms.find(fields={'_id': False, 'reservations': False}).sort("name", pymongo.ASCENDING)
        except:
            print "Unable to query database for user"
        
        for doc in cursor:
            rooms.append(doc)
            
        return rooms

    def get_event(self, room):
        
        query = {"name": room}
        projection = {"reservations": 1, "_id": 0}

        events = self.db.rooms.find_one(query, projection)
        if events is None:
            return json.dumps([]) 
        for event in events['reservations']:
            event['start'] = event['start'].isoformat()
            event['end'] = event['end'].isoformat()
            if type(event['until']) == int: # TODO: set until = start date in web.py or js in order to avoid this control.
                pass
            else:
                event['until'] = event['until'].isoformat()
            if event['repeat'] != 'never':
                event['backgroundColor'] = "#94ce8e"
                event['borderColor'] = "#66c65b"
            else:
                event['backgroundColor'] = "#6AA4C1"
                event['borderColor'] = "#3A87AD"
        return json.dumps(events["reservations"], default=json_util.default) # TODO: move json dumps in web.py? If it returns an array do I still need to perform json parse?

    def insert_event(self, room, events):

        self.db.rooms.update({"name": room}, {"$push": {"reservations": {"$each": events}}})
        #return events["reservations"]

    def update_event(self, room, event):

        if event['num'] is None:
            # Limitation: update on all events can modify only title.
            pipeline = [{"$match": {"name":"TRUST"}},
                        {"$unwind": "$reservations"},
                        {"$match": {"reservations.id": event['id']}},
                        {"$group": {"_id": "$reservations.id", "max_num": {"$max": "$reservations.num"}}}
                    ]
            result = self.db.rooms.aggregate(pipeline)
            max_num = int(result['result'][0]['max_num'])

            for num in range(max_num):
                print num
                query = { "name": room, "reservations.id": event['id'], "reservations.num": num }
                self.db.rooms.update( query, { "$set": { "reservations.$.title" : event["title"] } })
        else:
            query = { "name": room, "reservations.id": event['id'], "reservations.num": event['num']}
            event = { "$set": { "reservations.$.title" : event["title"],
                                "reservations.$.start" : event["start"],
                                "reservations.$.end" : event["end"] } }
            self.db.rooms.update(query, event)

    def remove_event(self, room, id, num):
        
        if num is None:
            num = "null"
        self.db.rooms.update({"name": room}, {"$pull": {"reservations": {"id": id, "num": num}}})

    def remove_event_from_here(self, room, id, here):
        
        self.db.rooms.update({"name": room}, {"$pull": {"reservations": {"id": id, "num": {"$gte": here}}}})
        
    def check_overlapping(self, room, id, start, start_hour, start_min, end_hour, end_min, until, week_day=None):
        
        pipeline = [
            { "$match": { "name": room }},
            { "$unwind": "$reservations" },
            { "$match": { "reservations.end": {"$lte": until}, "reservations.start": {"$gte": start} } },
            { "$project": { "_id": "$reservations.id", "day":{"$dayOfYear": "$reservations.start"}, "week_day": {"$dayOfWeek": "$reservations.start"},
                            "s_hour": {"$hour": "$reservations.start"}, "s_minutes": {"$minute": "$reservations.start"}, 
                            "e_hour": {"$hour": "$reservations.end" }, "e_minutes": {"$minute": "$reservations.end"} } },
            { "$project": { "day": 1,  "week_day": 1,
                            "sec_s": {"$add": [{"$multiply": ["$s_hour", 3600]}, {"$multiply": ["$s_minutes", 60]}]},
                            "sec_e": {"$add": [{"$multiply": ["$e_hour", 3600]}, {"$multiply": ["$e_minutes", 60]}]} } }

        ]

        if week_day is None:
            pipeline.append({ "$match":   { "_id": {"$ne": id}, "sec_s": {"$lt": end_hour*3600 + end_min*60}, "sec_e": {"$gt": start_hour*3600 + start_min*60} } })
        else:
            pipeline.append({ "$match":   { "_id": {"$ne": id}, "week_day": week_day, "sec_s": {"$lt": end_hour*3600 + end_min*60}, "sec_e": {"$gt": start_hour*3600 + start_min*60} } })
                            
        try:
            cursor = self.rooms.aggregate(pipeline)
        except:
            print "Unable to query database for user"    
        
        return cursor['result']

    def get_reservations_by_user(self, user):
        """
        Return all the reservations for a given user.
        """
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=7)
        pipeline = [
            {"$unwind": "$reservations"},
            {"$match": {"reservations.user": user,
                        "reservations.start": {"$lte": now+delta},
                        "reservations.end": {"$gte": now}
                    }},
            {"$project": { "_id": 0, "name": 1,
                           "reservations.start": 1, "reservations.end": 1,
                           "reservations.until": 1, "reservations.title": 1}},
            {"$sort": {"reservations.start": 1}}
        ]
        try:
            cursor = self.rooms.aggregate(pipeline)
        except:
            print "Unable to query database."
        return cursor['result']
