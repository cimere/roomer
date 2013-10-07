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


import pymongo


# The User Data Access Object handles all interactions with the User collection.
class UserDAO:

    def __init__(self, db):
        self.db = db
        self.users = self.db.users
        # self.SECRET = 'verysecret'

    def get_user_ids(self):

        users = {'username': []}

        try:
            cursor = self.users.find()
        except:
            print "Unable to query database for user"

        for doc in cursor:
            users['username'].append(doc['_id'])

        return users

    def get_user(self, id):

        try:
            user = self.users.find_one({"_id": id})
        except:
            print "Unable to query database for user"

        return user

    # Validates a user login. Returns user record or None
    def validate_login(self, username):

        user = None
        try:
            user = self.users.find_one({'_id': username})
        except:
            print "Unable to query database for user"

        if user is None:
            print "User not in database"
            return None

        # Looks good
        return user