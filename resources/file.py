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
from flask_jwt import jwt_required
from models.tokens import TokensModel
import config
from math import ceil
import time
import datetime
from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation, \
    MatchesPatternValidation, CustomSeriesValidation
from models.sl_logger import SlLogger

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['csv'])

logger = SlLogger.get_logger(__name__)


class File(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def get(self, uuid, page):
        data = File.parser.parse_args()
        logger.info("OAuth token is: {}".format(data['oauth_token']))
        if page < 1 or page > config.NO_OF_PAGES:
            logger.error("Page doesn't exists!")
            return {'message': "Page doesn't exists!"}, 400
        try:
            rows = TokensModel.find_by_uuid_slice(uuid, "device_store", page)
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!")
            return {"message": "Data search operation failed!"}, 500

        devices = []

        for row in rows:
            devices.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                            'va_name': row[5], 'domain': row[6]})
        logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
        logger.info(devices)
        logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
        logger.info(devices)

        if rows:
            return {'uuid': uuid,
                    'devices': devices}
        logger.error("Request with UUID: '{}' not found!".format(uuid))
        return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404

    @jwt_required()
    def post(self):
        File.parser.add_argument('registration_type',
                                 type=str,
                                 required=True,
                                 help="This field cannot be blank."
                                 )
        data = File.parser.parse_args()
        logger.info("OAuth token is: {}".format(data['oauth_token']))

        # Generate UUID to identify registration request
        uuid_str = str(uuid.uuid4())
        config.UUID = uuid_str
        # Valid registration_type list
        registration_list = ['sl', 'slr']
        if data['registration_type'] not in registration_list:
            logger.error("Registration type is not valid!")
            return {'message': "Registration type is not valid!"}, 400

        if 'file' not in request.files:
            logger.error("No File in the request!")
            return {"message": "No File in the request!"}, 400
        file = request.files['file']

        if file.filename == '':
            logger.error("No File selected!")
            return {'message': "No File selected!"}, 400

        if not File.allowed_file(file.filename):
            logger.error("File type not allowed! Only CSV files are allowed!")
            return {'message': "File type not allowed! Only CSV files are allowed!"}, 400

        # Validate each field/column of CSV file
        validate_flag, errors, df = File.validate_csv(file, data['registration_type'])
        if not validate_flag:
            logger.error("CSV file validation failed!: '{}'".format(errors))
            return {'message': "CSV file validation failed!: '{}'".format(errors)}, 400

        # Create dictionary for upload_info_store
        upload_info_dict = {'uuid': uuid_str, 'userid': config.USER_ID, 'filename': file.filename,
                            'type': data['registration_type'],
                            'timestamp': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                            'status': "csv_file_uploaded"}

        # Also set REGISTRATION_NAME as filename in config file
        config.REGISTRATION_NAME = file.filename

        # Create dictionaries for device_store, validation_store, device_status_store
        converted_json, converted_validation_json, converted_status_json = File.csv_to_json(df)

        # Enter data into the database store device_store
        if TokensModel.find_by_uuid(uuid_str, "device_store"):
            logger.info("Request with UUID: '{}' already exists.".format(uuid))
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, converted_json, "device_store")
        except Exception as e:
            print(e)
            logger.error("Data insert operation device_store failed!", exc_info=True)
            return {"message": "Data insert operation device_store failed!"}, 500

        # Enter data into the database store account_validation
        if TokensModel.find_by_uuid(uuid_str, "validation_store"):
            logger.info("Request with UUID: '{}' already exists.".format(uuid))
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, converted_validation_json, "validation_store")
        except Exception as e:
            print(e)
            logger.error("Data insert operation validation_store failed!", exc_info=True)
            return {"message": "Data insert operation validation_store failed!"}, 500

        # Enter data into the database store device_status_store
        if TokensModel.find_by_uuid(uuid_str, "device_status_store"):
            logger.info("Request with UUID: '{}' already exists.".format(uuid))
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, converted_status_json, "device_status_store")
        except Exception as e:
            print(e)
            logger.error("Data insert operation device_status_store failed!", exc_info=True)
            return {"message": "Data insert operation device_status_store failed!"}, 500

        try:
            if data['registration_type'] == 'slr':
                TokensModel.insert(uuid_str, converted_json, "slr_request_code_tbl")
        except Exception as e:
            print(e)
            logger.error("Data insert operation slr_request_code_tbl failed!", exc_info=True)
            return {"message": "Data insert operation slr_request_code_tbl failed!"}, 500

        # Enter data into the database store upload_info_store
        if TokensModel.find_by_uuid(uuid_str, "upload_info_store"):
            logger.info("Request with UUID: '{}' already exists.".format(uuid))
            return {'message': "Request with UUID: '{}' already exists.".format(uuid)}, 400

        try:
            TokensModel.insert(uuid_str, [upload_info_dict], "upload_info_store")
        except Exception as e:
            print(e)
            logger.error("Data insert operation failed!", exc_info=True)
            return {"message": "Data insert operation failed!"}, 500

        config.NO_OF_DEVICES = len(converted_json)
        config.NO_OF_PAGES = ceil(len(converted_json) / 10)
        new_request = {
            'uuid': uuid_str,
            'totalpages': config.NO_OF_PAGES,
            'message': 'File is uploaded!'
        }

        # For debugging
        logger.info(new_request)
        if TokensModel.find_by_uuid(uuid_str, "validation_store"):
            logger.info("Printed validation_store")
        if TokensModel.find_by_uuid(uuid_str, "device_status_store"):
            logger.info("Printed device_status_store")
        if TokensModel.find_by_uuid(uuid_str, "upload_info_store"):
            logger.info("Printed upload_info_store")
        logger.info("The request has been fulfilled and has resulted in one or more new resources being created")
        return new_request, 201

    @classmethod
    def validate_csv(cls, data, registration_type):
        df = pd.read_csv(data)
        logger.info("Printing dataframe before CSV validation...")
        logger.info(df)
        if registration_type == 'slr':
            csv_schema = Schema([
                Column('ipaddr', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                  MatchesPatternValidation(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'),
                                  CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('username', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                    CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('password', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                    CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('sa_name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                   CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('va_name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                   CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('domain', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                  CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('license', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
                Column('license_count', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
                Column('tftp_server_ip', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                          MatchesPatternValidation(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'),
                                          CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('tftp_server_path', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                            CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')])
            ])
        elif registration_type == 'sl':
            csv_schema = Schema([
                Column('ipaddr', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                  MatchesPatternValidation(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$'),
                                  CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('username', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                    CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('password', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                    CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('sa_name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                   CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('va_name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                   CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')]),
                Column('domain', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation(),
                                  CustomSeriesValidation(lambda x: x.str.len() > 0, 'Column is empty!')])
            ])

        errors = csv_schema.validate(df)

        if errors:
            errors_list = []
            for error in errors:
                print(error)
                errors_list.append(error)
            return False, errors_list, df
        else:
            return True, None, df

    @classmethod
    def csv_to_json(cls, df):
        # df = pd.read_csv(data)

        # Added to create device_uuid for each device in CSV file
        # define a function for the new column - device_uuid
        # Generate one more UUID to identify each device in registration request
        fn = lambda row: str(uuid.uuid4())
        # get column data with an index
        device_uuid_col = df.apply(fn, axis=1)
        logger.info("Printing device_store dataframe...")
        logger.info(df)
        df_validation = df.iloc[:, 3:6]
        logger.info("Printing device_validation dataframe...")
        logger.info(df_validation)
        # changed device_status_store schema to incl more fields
        df_status = df.iloc[:, 0:6]
        df_status['status'] = 'Unregistered'
        logger.info("Printing device_status_store dataframe...")
        logger.info(df_status)
        # After all dataframes are ready apply new device_uuid column to df & df_status
        # For df dataframe assign values to column 'device_uuid'
        df = df.assign(device_uuid=device_uuid_col.values)
        df = df.to_json(orient='records')
        dfjson = json.loads(df)
        df_validation = df_validation.to_json(orient='records')
        dfvalidjson = json.loads(df_validation)
        # For dt_status dataframeassign values to column 'device_uuid'
        df_status = df_status.assign(device_uuid=device_uuid_col.values)
        df_status = df_status.to_json(orient='records')
        dfstatusjson = json.loads(df_status)
        logger.info("Printing device_status_store json...")
        logger.info(dfstatusjson)
        return dfjson, dfvalidjson, dfstatusjson

    @classmethod
    def allowed_file(cls, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Fileuploadstatus(Resource):

    @jwt_required()
    def get(self, uuid, page):

        try:
            rows_uuid = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!")
            return {"message": "Data search operation failed!"}, 500

        if not rows_uuid:
            logger.error("Request with UUID: '{}' doesn't exists.".format(uuid))
            return {'message': "Request with UUID: '{}' doesn't exists.".format(uuid)}, 404

        config.NO_OF_DEVICES = len(rows_uuid)
        config.NO_OF_PAGES = ceil(config.NO_OF_DEVICES / 10)

        logger.info("Pagination: UUID for this request is: {}".format(uuid))
        logger.info("Pagination: Total number of pages: {}".format(config.NO_OF_PAGES))
        logger.info("Pagination: Page number requested is: {}".format(page))

        if page < 1 or page > config.NO_OF_PAGES:
            logger.error("Page doesn't exists!")
            return {'message': "Page doesn't exists!"}, 400
        try:
            rows = TokensModel.find_by_uuid_slice(uuid, page, "device_store")
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!")
            return {"message": "Data search operation failed!"}, 500

        devices = []

        for row in rows:
            devices.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                            'va_name': row[5], 'domain': row[6]})
        logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
        logger.info(devices)
        if rows:
            logger.info("Request with UUID: '{}' found!".format(uuid))
            return {'uuid': uuid,
                    'totalpages': config.NO_OF_PAGES,
                    'devices': devices}
        logger.error("Request with UUID: '{}' not found!".format(uuid))
        return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404
