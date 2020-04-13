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
import config
from math import ceil
from models.slr import slr
from models.tokens import TokensModel
from flask_jwt import jwt_required
from models.sl_logger import SlLogger

# Constants
NUMBER_OF_DEVICES_PER_PAGE = 10
SLR_REQUEST_CODE_TABLE_NAME = "slr_request_code_tbl"
# dict
col = {0: "uuid", 1: "ipaddr", 2: "username", 3: "password", 4: "sa_name", 5: "va_name", 6: "domain"}


logger = SlLogger.get_logger(__name__)


class SlrUpdateStatus(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del self.slr
        pass

    @jwt_required()
    def post(self, uuid, page):
        return self.generate_output(uuid, page)

    @jwt_required()
    def get(self, uuid, page):
        return self.generate_output(uuid, page)

    def generate_output(self, uuid, page):
        slr_table = SLR_REQUEST_CODE_TABLE_NAME
        response = {}
        try:
            total_rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e:
            print(e)
            logger.error({"message": "Data search operation failed!"}, exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        config.NO_OF_DEVICES = len(total_rows)
        config.NO_OF_PAGES = ceil(config.NO_OF_DEVICES / NUMBER_OF_DEVICES_PER_PAGE)
        response["totalpages"] = config.NO_OF_PAGES
        response["devices"] = []

        try:
            rows = TokensModel.find_by_uuid_slice(uuid, page, "device_store")
        except Exception as e:
            print(e)
            logger.error({"message": "Data search operation failed!"}, exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        for row in rows:
            ip_address = row[1]
            try:
                val = self.slr.find_by_uuid_ipaddr(uuid, slr_table, ip_address)
            except Exception as e:
                print(e)
                logger.error({"message": "Data search operation failed!"}, exc_info=True)
                return {"message": "Data search operation failed!"}, 500

            device_dict = {}
            for i in col:
                device_dict[col[i]] = row[i]
            logger.info(val)
            device_dict['s2Status'] = ""
            device_dict['s3Status'] = ""
            device_dict['s4Status'] = ""
            try:
                device_dict['s2Status'] = val[0][2]
                device_dict['s3Status'] = val[0][3]
                device_dict['s4Status'] = val[0][4]
            except Exception as e:
                print(e)

            response["devices"].append(device_dict)
            del device_dict

        logger.info("Final response")
        logger.info(response)
        return response, 201
