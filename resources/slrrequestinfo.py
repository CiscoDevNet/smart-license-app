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


class SlrRequestInfo(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del self.slr
        pass

    @jwt_required()
    def get(self, uuid):
        try:
            rows = TokensModel.find_by_uuid(uuid, "upload_info_store")
        except Exception as e:
            print(e)
            logger.error({"message": "Data search operation failed!"}, exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        return {'status': rows[0][5]}, 201
