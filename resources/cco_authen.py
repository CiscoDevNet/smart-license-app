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

from pathlib import Path
import requests
import yaml
from flask_restful import Resource, reqparse, request

import config

home = str(Path.home())


class UserCco(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self):

        try:
            with open(home+"/config.yaml", 'r') as yamlfile:
                cfg = yaml.load(yamlfile)
            client_id = cfg['api_keys']['client_id']
            client_secret = cfg['api_keys']['client_secret']

        except:
            return {'message': 'Not able to find config.yaml file!'}, 401

        print("Printing raw request..")
        print(request.__dict__)

        data = UserCco.parser.parse_args()
        uri = "https://cloudsso.cisco.com/as/token.oauth2"
        body = {"client_id": client_id, "client_secret": client_secret, "username": data['username'],
                "password": data['password'], "grant_type": "password"}
        config.USER_ID = data['username']
        print("User ID:", config.USER_ID)
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", uri, headers=headers, params=body)
        print("Now printing response....")
        print(response.text)
        try:
            token_type = response.json()['token_type']
            config.OAUTH_TOKEN = response.json()['access_token']
            # We are not validating refresh_token because we are asking user not to select refresh token
            # option while registering for grant assuming that CSSM never use refresh_token
            # refresh_token = response.json()['refresh_token']
            expires_in = response.json()['expires_in']
            print("====>>>>    Success: Got OAuth Token    <<<<====\n\n")
        except:
            return {'message': 'Please check your username/password!'}, 401

        return {'access_token': config.OAUTH_TOKEN,
                # 'refresh_token': refresh_token,
                'token_type': token_type,
                'expires_in': expires_in}
