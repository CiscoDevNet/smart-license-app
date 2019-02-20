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

from flask_restful import Resource
from models.slr import slr
from models.tokens import TokensModel

slr_req_tbl = "slr_request_code_tbl"
slr_author_tbl = "slr_author_code_tbl"
database_err = {"message": "Data search operation failed!"}
s_start = "Status Started"
s_done = "Status Done"
s_authc_fail = "Status Authc Fail"
s_prompt = "Status Prompt Missing"
status_complete = {"status": s_done}
status_progress = {"status": "Status In Progress"}


class slrrequestinfo(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass;

    def __del__(self):
        del(self.slr)
        pass;

    def get(self, uuid):
        try:
            rows = TokensModel.find_by_uuid(uuid, "upload_info_store")
        except Exception as e:
            print(e)
            return database_err, 500

        return {'status': rows[0][5]}, 201
