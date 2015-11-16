#
# Module for helper functions.
#

import time
import datetime
import logging


def get_reservation_day(reservation):
    return reservation['reservations']['start'].strftime("%A %d")


def get_reservation_start(reservation):
    return reservation['reservations']['start'].strftime("%H:%M")


def get_reservation_end(reservation):
    return reservation['reservations']['end'].strftime("%H:%M")


def epoch_to_iso(seconds_since_epoch):
    return datetime.datetime.fromtimestamp(seconds_since_epoch)


def ISO_str_to_date(string):
    #  struct = time.strptime(string, "%a %b %d %Y %H:%M:%S GMT+0200 (CEST)")
    #  unix = time.mktime(struct)
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
    if 'start' in d.keys():
        d['start'] = ISO_str_to_date(d['start'])
    if 'end' in d.keys():
        d['end'] = ISO_str_to_date(d['end'])
    if 'num' in d.keys():
        d['num'] = int(d['num'])
    if 'allDay' in d.keys():
        # d['allDay'] = eval(string.capitalize(d['allDay']))
        d['allDay'] = eval(d['allDay'].capitalize())
    return d


def format_room_data(data):
    ''' list of dict --> list of dict
        in dict: {'tel', 'name', 'people', 'whiteboard', 'vdc', 'type': 'desc'}
        out dict: {'name', 'desc'}
    '''
    desc = "Fino a "+str(data['people'])+" persone, "+data['whiteboard']+"."
    if data['tel'] is not None:
        desc += "Interno: "+str(data['tel'])+"."
    if data['vdc'] is not None:
        desc += "VDC: "+data['vdc']+". "
    return {"name": data["name"], "desc": desc, "bookable": data["bookable"]}


def is_overlapping(request, rooms):

    id = request.forms.get("id")
    room = request.forms.get("room")
    repeat = request.forms.get("repeat")
    start = ISO_str_to_date(request.forms.get("start"))
    end = ISO_str_to_date(request.forms.get("end"))
    if repeat != "never":
        # recurring event, check for overlapping
        until = str_to_date(request.forms.get("until"))
        if repeat == "week":
            # on mongodb week starts on Sunday
            week_day = start.isoweekday() + 1
        else:
            week_day = None

        overlapping = rooms.check_overlapping(room, id, start,
                                              start.hour, start.minute,
                                              end.hour, end.minute,
                                              until, week_day)
        if overlapping == []:
            # not overlapping
            # logging.info("No overlapping events found.")
            return False
        else:
            overlapping_events = []
            for event in overlapping:
                overlapping_events.append(
                    day_to_date(event['day']).isoformat())
            # logging.info("Overlapping events: %s", repr(overlapping_events))
            return True


def get_free_slot(duration):
    # print rooms.get_free_slots(duration)
    # TO DO: to be implemented
    pass


def logger(func):
    ''' Decorator '''
    func_name = str(func).split()[1]
    def log_and_profile(*xargs):
        # TO DO: implement profiler with time diff.
        logging.info("Start: " + func_name + " " + str(xargs))
        ret = func(*xargs)
        logging.info("End: " + func_name)
        return ret
    return log_and_profile
