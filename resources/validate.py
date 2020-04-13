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


import requests
from flask_restful import Resource, reqparse
from models.tokens import TokensModel
from models.sl_logger import SlLogger

logger = SlLogger.get_logger(__name__)


class Validate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self, uuid):
        data = Validate.parser.parse_args()
        rows = TokensModel.find_by_uuid(uuid, "validation_store")
        if not rows:
            logger.error("Request with UUID: '{}' doesn't exists.".format(uuid))
            return {'message': "Request with UUID: '{}' doesn't exists.".format(uuid)}, 404

        domains = TokensModel.find_by_uuid_distinct(uuid, "validation_store")

        for domain in domains:
            url = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/" + domain + \
                  "/customer/virtual-accounts"
            headers = {
                "Authorization": data['oauth_token'],
                "Content-Type": "application/json"
            }
            response = requests.request("GET", url, headers=headers)
            logger.info(response.json())

        logger.info("success")
        return {"message": "success"}, 201
