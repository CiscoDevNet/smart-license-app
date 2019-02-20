# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at
#
#                https://developer.cisco.com/docs/licenses
#
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

"""@package databasehandler
Used to communicate with sqllite

Usage:
dbmgr = databasehandler()
for row in dbmgr.query("select * from device_store where username=\"" + "admin" + "\""):
    print (row)
del(dbmgr)
"""

import sqlite3

class databasehandler(object):
    def __init__(self, db="data.db"):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def query(self, arg):
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()

