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
from bson.objectid import ObjectId
from utils import logger

# The Group Data Access Object handles all interactions with
# the Groups collection.


class groupDAO:

    @logger
    def __init__(self, db):
        self.db = db
        self.groups = self.db.groups

    @logger
    def get(self, group_id):
        '''
        Given a group id, return the corresponding document.
        '''
        try:
            group = self.groups.find_one({"_id": ObjectId(group_id)})
        except:
            print("Unable to query database for groups")
        return group

    @logger
    def get_all(self):
        '''
        Return all the groups.
        '''
        groups = []
        try:
            cursor = self.groups.find()
        except:
            print("Unable to query database for groups")
        for doc in cursor:
            groups.append(doc)
        return groups

    def add(group_name):
        """
        Add a new group to the collection.
        """
        print("Not implemented yet.")

    def remove(group_id):
        """
        Remove a group from the collection.
        """
        print("Not implemented yet.")

    def change_name(group_id, group_name):
        """
        Change the group name.
        """
        print("Not implemented yet.")

    def add_room(group_id, room_id):
        """
        Add a room to the group.
        """
        print("Not implemented yet.")

    def remove_room(group_id, room_id):
        """
        Remove a room from the group.
        """
        print("Not implemented yet.")
