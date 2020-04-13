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
from flask_jwt import jwt_required
from models.sl_logger import SlLogger

logger = SlLogger.get_logger(__name__)


class FetchAuthCodesStatus(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del self.slr
        pass

    @jwt_required()
    def get(self, uuid):
        try:
            rows = TokensModel.find_by_uuid(uuid, "slr_request_code_tbl")
        except Exception as e:
            print(e)
            logger.error("Data search operation failed!", exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        if rows:
            # Counter for total no of devices for which auth codes needs to be generated
            total_devices = len(rows)
            not_started_counter = 0
            started_counter = 0
            failed_counter = 0
            processed_counter = 0
            # Updated for all status types
            for row in rows:
                if row[3] == "NS":
                    not_started_counter += 1
                elif row[3] == "Started":
                    started_counter += 1
                elif row[3] == "Completed":
                    processed_counter += 1
                elif "Error" in row[3]:
                    failed_counter += 1
                    processed_counter += 1
            if processed_counter == total_devices:
                status = "Completed"
            elif not_started_counter == total_devices:
                status = "NotStarted"
            else:
                status = "In-Progress"
            return {'message': 'Successfully fetched status of Auth Codes!',
                    'progress': status,
                    'total': total_devices,
                    'failed': failed_counter,
                    'processed': processed_counter}, 200
        else:
            logger.error("Request with UUID: '{}' not found!".format(uuid))
            return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404
