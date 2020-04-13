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
from flask_jwt import jwt_required
import urllib3
import config
from models.tokens import TokensModel
from models.sl_logger import SlLogger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logger = SlLogger.get_logger(__name__)


class Registrations(Resource):

    @jwt_required()
    def get(self):
        # Return last 10 registration requests executed
        logger.info("In class registrations - User ID: {}".format(config.USER_ID))

        try:
            rows = TokensModel.find_last_records(config.USER_ID, "upload_info_store", "timestamp")
        except Exception as e:
            logger.error(e)
            logger.error('Data search operation failed!')
            return {"message": "Data search operation failed!"}, 500

        devices = []

        for row in rows:
            devices.append({'uuid': row[0], 'filename': row[2], 'registration_type': row[3], 'timestamp': row[4],
                            'status': row[5]})
        logger.info('==>> Printing devices from within get method for resource: Tokens <<==')
        logger.info(devices)
        if rows:
            return {'message': 'Last registrations',
                    'devices': devices}
        logger.error('Request for last 10 registrations not found!')
        return {"message": "Request for last 10 registrations not found!"}, 404
