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

import pandas as pd
import json
import uuid
from flask import request
from flask_restful import Resource, reqparse
from models.tokens import TokensModel
import config
from math import ceil
import time
import datetime

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['csv'])


class File(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def get(self, uuid, page):
        data = File.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])
        if page < 1 or page > config.NO_OF_PAGES:
            return {'message': "Page doesn't exists!"}, 400
        try:
            rows = TokensModel.find_by_uuid_slice(uuid, "device_store", page)
        except:
            return {"message": "Data search operation failed!"}, 500

        devices = []

        for row in rows:
            devices.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                            'va_name': row[5], 'domain': row[6]})
        print("==>> Printing devices from within get method for resource: Tokens <<==")
        print(devices)
        if rows:
            return {'uuid': uuid,
                    'devices': devices}
        return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404

    def post(self):
        File.parser.add_argument('registration_type',
                                 type=str,
                                 required=True,
                                 help="This field cannot be blank."
                                 )
        data = File.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])

        uuid_str = str(uuid.uuid4())
        if 'file' not in request.files:
            return {"message": "No File in the request!"}, 400
        file = request.files['file']

        if file.filename == '':
            return {'message': "No File selected!"}, 400

        if not File.allowed_file(file.filename):
            return {'message': "File type not allowed! Only CSV files are allowed!"}, 400

        # Create dictionary for upload_info_store
        upload_info_dict = {}
        upload_info_dict['uuid'] = uuid_str
        upload_info_dict['userid'] = config.USER_ID
        upload_info_dict['filename'] = file.filename
        upload_info_dict['type'] = data['registration_type']
        upload_info_dict['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        upload_info_dict['status'] = "csv_file_uploaded"

        # Create dictionaries for device_store, validation_store, device_status_store
        converted_json, converted_validation_json, converted_status_json = File.csv_to_json(file)

        # Enter data into the database store device_store
        if TokensModel.find_by_uuid(uuid_str, "device_store"):
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, converted_json, "device_store")
        except Exception as e:
            print(e)
            return {"message": "Data insert operation device_store failed!"}, 500

        # Enter data into the database store account_validation
        if TokensModel.find_by_uuid(uuid_str, "validation_store"):
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, converted_validation_json, "validation_store")
        except Exception as e:
            print(e)
            return {"message": "Data insert operation validation_store failed!"}, 500

        # Enter data into the database store device_status_store
        if TokensModel.find_by_uuid(uuid_str, "device_status_store"):
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, converted_status_json, "device_status_store")
        except Exception as e:
            print(e)
            return {"message": "Data insert operation device_status_store failed!"}, 500

        try:
            if data['registration_type'] == 'slr':
                TokensModel.insert(uuid_str, converted_json, "slr_request_code_tbl")
        except Exception as e:
            print (e)
            return {"message": "Data insert operation slr_request_code_tbl failed!"}, 500

        # Enter data into the database store upload_info_store
        if TokensModel.find_by_uuid(uuid_str, "upload_info_store"):
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, [upload_info_dict], "upload_info_store")
        except Exception as e:
            print(e)
            return {"message": "Data insert operation failed!"}, 500

        config.NO_OF_DEVICES = len(converted_json)
        config.NO_OF_PAGES = ceil(len(converted_json)/10)
        new_request = {
                'uuid': uuid_str,
                'totalpages': config.NO_OF_PAGES,
                'message': 'File is uploaded!'
        }

        # For debugging
        print(new_request)
        if TokensModel.find_by_uuid(uuid_str, "validation_store"):
            print("Printed validation_store")
        if TokensModel.find_by_uuid(uuid_str, "device_status_store"):
            print("Printed device_status_store")
        if TokensModel.find_by_uuid(uuid_str, "upload_info_store"):
            print("Printed upload_info_store")

        return new_request, 201

    @classmethod
    def csv_to_json(cls, data):
        df = pd.read_csv(data)
        print("Printing device_store dataframe...")
        print(df)
        df_validation = df.iloc[:, 3:6]
        print("Printing device_validation dataframe...")
        print(df_validation)
        # changed device_status_store schema to incl more fields
        df_status = df.iloc[:, 0:6]
        df_status['status'] = 'Unregistered'
        print("Printing device_status_store dataframe...")
        print(df_status)
        df = df.to_json(orient='records')
        dfjson = json.loads(df)
        df_validation = df_validation.to_json(orient='records')
        dfvalidjson = json.loads(df_validation)
        df_status = df_status.to_json(orient='records')
        dfstatusjson = json.loads(df_status)
        print("Printing device_status_store json...")
        print(dfstatusjson)
        return dfjson, dfvalidjson, dfstatusjson

    @classmethod
    def allowed_file(cls, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Fileuploadstatus(Resource):

    def get(self, uuid, page):

        try:
            rows_uuid = TokensModel.find_by_uuid(uuid, "device_store")
        except:
            return {"message": "Data search operation failed!"}, 500

        if not rows_uuid:
            return {'message': "Request with UUID: '{}' doesn't exists.".format(uuid)}, 404

        config.NO_OF_DEVICES = len(rows_uuid)
        config.NO_OF_PAGES = ceil(config.NO_OF_DEVICES/10)
        print("Pagination: UUID for this request is:", uuid)
        print("Pagination: Total number of pages:", config.NO_OF_PAGES)
        print("Pagination: Page number requested is:", page)

        if page < 1 or page > config.NO_OF_PAGES:
            return {'message': "Page doesn't exists!"}, 400
        try:
            rows = TokensModel.find_by_uuid_slice(uuid, page, "device_store")
        except:
            return {"message": "Data search operation failed!"}, 500

        devices = []

        for row in rows:
            devices.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                            'va_name': row[5], 'domain': row[6]})
        print("==>> Printing devices from within get method for resource: Tokens <<==")
        print(devices)
        if rows:
            return {'uuid': uuid,
                    'totalpages': config.NO_OF_PAGES,
                    'devices': devices}
        return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404
