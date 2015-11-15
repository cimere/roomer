from bson import json_util
import datetime
import pymongo
import json
import sys
# from bson.objectid import ObjectId


# The User Data Access Object handles all
# interactions with the User collection.
class RoomDAO:

    def __init__(self, db):
        self.db = db
        self.rooms = self.db.rooms
        # self.SECRET = 'verysecret'

    def get_room_id(self, room_name):
        '''
        Given the room's name, return the room id.
        '''
        try:
            room = self.rooms.find_one({"name": room_name},
                                       projection={'_id': True})
        except Exception as e:
            print("Unable to query database for user", e)
        return None if room is None else room['_id']

    def get_room(self, name):
        '''
        Given the room's name, return the whole room document.
        '''
        try:
            room = self.rooms.find_one({"name": name},
                                       projection={'reservations': False})
        except:
            print("Unable to query database for user")
        print("get_room returned %s bytes" % sys.getsizeof(room))
        return room

    def get_rooms(self, rooms_list):
        '''
        Return all rooms details except reservations.
        '''
        rooms = []
        try:
            cursor = self.rooms.find(projection={'reservations': False}
                                     ).sort("name", pymongo.ASCENDING)
            for doc in cursor:
                if str(doc['_id']) in rooms_list:
                    rooms.append(doc)
        except:
            print("Unable to query database for user")
        print("get_rooms returned %s bytes" % sys.getsizeof(rooms))
        return rooms

    def get_events(self, room, start=None, end=None):
        '''
        Given a room name, return all its reservations.
        '''
        events = {}
        events["reservations"] = []
        pipeline = [
            {"$match": {"name": room}},
            {"$unwind": "$reservations"},
            {"$match": {"reservations.end": {"$lte": end},
                        "reservations.start": {"$gte": start}}}
        ]
        # events = self.db.rooms.find_one(query, projection)
        try:
            results = self.rooms.aggregate(pipeline)
        except Exception as e:
            print("Unable to query database for user", e)
        if results is None:
            return json.dumps([])
        for res in results:
            event = res['reservations']
            event['start'] = event['start'].isoformat()
            event['end'] = event['end'].isoformat()
            # TODO: set until = start date in web.py or js in order
            # to avoid the following check.
            if type(event['until']) == int:
                pass
            else:
                event['until'] = event['until'].isoformat()
            if event['repeat'] != 'never':
                event['backgroundColor'] = "#94ce8e"
                event['borderColor'] = "#66c65b"
            else:
                event['backgroundColor'] = "#6AA4C1"
                event['borderColor'] = "#3A87AD"
            events["reservations"].append(event)
        # TODO: move json dumps in web.py? If it returns an array do
        # I still need to perform json parse?
        print("get_events returned %s bytes" % sys.getsizeof(events))
        return json.dumps(events["reservations"], default=json_util.default)

    def insert_event(self, room, events):
        '''
        Insert an event in a room.
        '''
        self.db.rooms.update_one({"name": room},
                                 {"$push": {"reservations": {"$each": events}}})
        # return events["reservations"]

    def update_event(self, room, event):
        '''
        Update an event.
        '''
        if event['num'] is None:
            # Limitation: update on all events can modify only title.
            pipeline = [{"$match": {"name": event['room']}},
                        {"$unwind": "$reservations"},
                        {"$match": {"reservations.id": event['id']}},
                        {"$group": {"_id": "$reservations.id",
                                    "max_num": {"$max": "$reservations.num"}}}
                        ]
            result = self.db.rooms.aggregate(pipeline)
            max_num = list(result)['max_num']
            for num in range(max_num):
                query = {"name": room,
                         "reservations.id": event['id'],
                         "reservations.num": num}
                self.db.rooms.update_one(query,
                                         {"$set":
                                          {"reservations.$.title":
                                           event["title"]}}
                                         )
        else:
            query = {"name": room, "reservations.id": event['id']}
            event = {"$set": {"reservations.$.title": event["title"],
                              "reservations.$.start": event["start"],
                              "reservations.$.end": event["end"]}
                     }
            self.db.rooms.update_one(query, event)

    def remove_event(self, room, id, num):
        '''
        Remove an event.
        '''
        if num is None:
            num = "null"
        self.db.rooms.update_one({"name": room},
                                 {"$pull":
                                 {"reservations": {"id": id, "num": num}}})

    def remove_event_from_here(self, room, id, here):
        '''
        Remove a lot of events.
        '''
        self.db.rooms.update_one({"name": room},
                                 {"$pull":
                                  {"reservations":
                                   {"id": id, "num": {"$gte": here}}}})

    def check_overlapping(self, room, id, start, start_hour, start_min,
                          end_hour, end_min, until, week_day=None):
        '''
        Check if a recurring event overlaps in some point with
        some other events.
        '''
        pipeline = [
            {"$match": {"name": room}},
            {"$unwind": "$reservations"},
            {"$match": {"reservations.end": {"$lte": until},
                        "reservations.start": {"$gte": start}}},
            {"$project": {"_id": "$reservations.id",
                          "day": {"$dayOfYear": "$reservations.start"},
                          "week_day": {"$dayOfWeek": "$reservations.start"},
                          "s_hour": {"$hour": "$reservations.start"},
                          "s_minutes": {"$minute": "$reservations.start"},
                          "e_hour": {"$hour": "$reservations.end"},
                          "e_minutes": {"$minute": "$reservations.end"}}},
            {"$project": {"day": 1,
                          "week_day": 1,
                          "sec_s": {"$add": [{"$multiply": ["$s_hour", 3600]},
                                             {"$multiply": ["$s_minutes", 60]}]
                                    },
                          "sec_e": {"$add": [{"$multiply": ["$e_hour", 3600]},
                                             {"$multiply": ["$e_minutes", 60]}]
                                    }}}
        ]
        if week_day is None:
            pipeline.append({"$match":
                             {"_id": {"$ne": id},
                              "sec_s": {"$lt": end_hour*3600 + end_min*60},
                              "sec_e": {"$gt": start_hour*3600 + start_min*60}
                              }})
        else:
            pipeline.append({"$match":
                             {"_id": {"$ne": id},
                              "week_day": week_day,
                              "sec_s": {"$lt": end_hour*3600 + end_min*60},
                              "sec_e": {"$gt": start_hour*3600 + start_min*60}
                              }})
        try:
            results = self.rooms.aggregate(pipeline)
        except:
            print("Unable to query database for user")
        return list(results)

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
                        "reservations.end": {"$gte": now}}},
            {"$project": {"_id": 0, "name": 1,
                          "reservations.start": 1, "reservations.end": 1,
                          "reservations.until": 1, "reservations.title": 1}},
            {"$sort": {"reservations.start": 1}}
        ]
        try:
            cursor = self.rooms.aggregate(pipeline)
        except:
            print("Unable to query database.")
        return list(cursor)
