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

from flask_restful import Resource, reqparse
import config
from math import ceil
from models.slr import slr
from models.tokens import TokensModel

req_token_command="pwd"
msg_name = "message"
message = {}
device = "devices"
database_err = {"message": "Data search operation failed!"}
invalid_request = {"message": "Invalid request for slr!"}
col = {}
slr_request_code_tbl = "CREATE TABLE IF NOT EXISTS slr_request_code_tbl (uuid text, ipaddr text, username text," \
                       " password text, sa_name text, va_name text, authz_req_code text, status text)"
uuid = 0
ip_addr = 1
username = 2
password = 3
sa_name = 4
va_name = 5
domain = 6
col[0] = "uuid"
col[1] = "ipaddr"
col[2] = "username"
col[3] = "password"
col[4] = "sa_name"
col[5] = "va_name"
col[6] = "domain"
pages = "totalpages"
slr_req_tbl = "slr_request_code_tbl"
slr_author_tbl = "slr_author_code_tbl"
reqcode = "reqcode"
authkey = "authkey"
message[reqcode] = "Request code"
message[authkey] = "Auth key"
num_of_device_per_page = 10


class slrgeneraterequestcode(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass;

    def __del__(self):
        del(self.slr)
        pass;

    def post(self, uuid, page):
        return self.generate_output(uuid, page)

    def get(self, uuid, page):
        return self.generate_output(uuid, page)

    def generate_output(self, uuid, page):
        slr_table = None
        slr_table = slr_req_tbl

        if (slr_table == None):
            return invalid_request, 404

        response = {};
        try:
            total_rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e: 
            print(e)
            return database_err, 500

        config.NO_OF_DEVICES = len(total_rows)
        config.NO_OF_PAGES = ceil(config.NO_OF_DEVICES/num_of_device_per_page)
        response[pages] = config.NO_OF_PAGES

        response[device] = []

        try:
            rows = TokensModel.find_by_uuid_slice(uuid, page, "device_store")
        except Exception as e: 
            print(e)
            return database_err, 500

        for row in rows:
            ip_address = row[ip_addr]
            try:
                val = self.slr.find_by_uuid_ipaddr(uuid, slr_table, ip_address)
            except Exception as e: 
                print(e)
                return database_err, 500

            device_dict = {}
            for i in col:
                device_dict[col[i]] = row[i]
            print(val)
            device_dict['s2Status'] = ""
            device_dict['s3Status'] = ""
            device_dict['s4Status'] = ""
            try : 
                device_dict['s2Status'] = val[0][2]
                device_dict['s3Status'] = val[0][3]
                device_dict['s4Status'] = val[0][4]
            except Exception as e:
                print (e)

            response[device].append(device_dict)
            del(device_dict)
        
        print("Final response")
        print(response)
        return (response), 201

