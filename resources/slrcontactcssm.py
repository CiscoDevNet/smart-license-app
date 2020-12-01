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
import time

from flask import json
from flask_restful import Resource, reqparse

import config
from models.slr import slr
from models.tokens import TokensModel
from flask_jwt import jwt_required
import backoff
import requests
import threading
from models.sl_logger import SlLogger
from resources.slrrequestcode import SlrRequestCode
from resources.slrimportcodes import ImportCodes


# Constants
SLR_REQUEST_CODE_TABLE_NAME = "slr_request_code_tbl"
URL_PREFIX = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/{}/virtual-accounts/{}" \
             "/reserve-licenses"

# Global variables
slr_table_name = SLR_REQUEST_CODE_TABLE_NAME
delim = " "

logger = SlLogger.get_logger(__name__)


class SlrContactCSSM(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del self.slr
        pass

    def send_request_cssm(self, uuid, oauthToken):
        logger.info("contact CSSM debugs")
        threads = []
        slr_table = SLR_REQUEST_CODE_TABLE_NAME
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e:
            print(e)
            logger.error({"message": "Data search operation failed!"}, exc_info=True)
            return {"message": "Data search operation failed!"}, 500
        if not rows:
            logger.error("No Devices with this UUID")
            return ({"request": "No Devices with this UUID"}), 400

        for row in rows:
            logger.info("Launching threads to get auth tokens")
            # Updating the response status to Step 3 started
            response_update = {'status': "S3s"}
            TokensModel.update(uuid, response_update, "upload_info_store")
            self.slr.update_status(slr_table, row[0], row[1], "Started", "step2")
            ''' Bulk DLC Call'''
            if TokensModel.find_fileType(uuid) != "sl" and TokensModel.find_slr_type(uuid) == "slr":
                domain_name, dlcRequest = SlrRequestCode.get_dlc_conversion_api_body(uuid)
                if dlcRequest:
                    self.slr_bulkDLC(uuid, domain_name, dlcRequest, config.OAUTH_TOKEN)
            if TokensModel.find_fileType(uuid) != "sl" and TokensModel.find_slr_type(uuid) == "slrx":
                domain_name, dlcRequest = ImportCodes.get_dlc_payload(uuid)
                if dlcRequest:
                    self.slr_bulkDLC(uuid, domain_name, dlcRequest, config.OAUTH_TOKEN)
            th = threading.Thread(target=SlrContactCSSM.get_cssm_response, args=(row[6], row[5], oauthToken, row[1],
                                                                                 row[0]))
            th.start()
            threads.append(th)
        logger.info({"request": "accepted"})
        return {"request": "accepted"}, 201

    @jwt_required()
    def post(self, uuid):
        data = SlrContactCSSM.parser.parse_args()
        logger.info("OAuth token is: {}".format(data['oauth_token']))
        return self.send_request_cssm(uuid, data['oauth_token'])

    @classmethod
    def get_cssm_response(cls, domain_name, va_name, oauthToken, device_ip, uuid):
        final_msg = ""
        url = URL_PREFIX.format(domain_name, va_name)
        logger.info("Value of the rest api url is ")
        logger.info(url)

        headers = {
            "Authorization": "Bearer " + oauthToken,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        s = slr("", "", "")
        try:
            i = 0
            val = s.find_by_uuid_ipaddr(uuid, slr_table_name, device_ip)
            if val[0][2] != "Completed":
                logger.info(val[0][2])
                logger.info(val)
                logger.error("Error in previous step")
                s.update_status(slr_table_name, uuid, device_ip, "Error in previous step", "step2")
                rows = s.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Started", "step2")
                if len(rows) == 0:
                    # Updating the response status to Step 3 Complete
                    response_update = {'status': "S3c"}
                    TokensModel.update(uuid, response_update, "upload_info_store")
                return
            tags = val[0][11]
            licenses = []
            try:
                license_count = s.get_license_count(val[0]).split(delim)
                logger.info(license_count)
                for tag in tags.split(delim):
                    if int(license_count[i]) > 0:
                        try:
                            licenses.append(
                                {"entitlementTag": tag, "quantity": license_count[i], "precedence":
                                    "LONGEST_TERM_FIRST"})
                        except Exception as e:
                            s.update_status(slr_table_name, uuid, device_ip,
                                            "License count and licenses are not set properly",
                                            "step2")
                            print(e)
                            logger.error("License count and licenses are not set properly", exc_info=True)
                            rows = s.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Started", "step2")
                            if len(rows) == 0:
                                # Updating the response status to Step 3 Complete
                                response_update = {'status': "S3c"}
                                TokensModel.update(uuid, response_update, "upload_info_store")
                    i = i + 1
            except Exception as e:
                print(e)
                s.update_status(slr_table_name, uuid, device_ip, "License is not separated by spaces", "step2")
                logger.error("License is not separated by spaces", exc_info=True)
                rows = s.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Started", "step2")
                if len(rows) == 0:
                    # Updating the response status to Step 3 Complete
                    response_update = {'status': "S3c"}
                    TokensModel.update(uuid, response_update, "upload_info_store")
                return

            body = {"reservationRequests": [
                {"reservationCode": val[0][5], "reservationType": "SPECIFIC", "licenses": licenses}]}
            logger.info("Reservation request for uuid " + uuid + " for device with ip " + device_ip)
            logger.info(headers)
            logger.info(body)
            a = json.dumps(body)
            # New call added for response with retries
            response = SlrContactCSSM.send_post_with_retries(url, a, headers, 30)
            # response = requests.request("POST", url, data=a, headers=headers, timeout=10)
            logger.info("Now printing response.json & contents.decode as per old call...")
            logger.info(response.json())
            logger.info(response.content.decode())
            if val[0][3] == "Completed":
                logger.info("Already marked step as completed, don't proceed further. This can happen when rest call \
                            takes time. It is more of a race condition, seen once in my testing. Handling for the same")
                return
            try:
                msg = response.json()
                logger.info(msg['status'])
                if msg['status'] == "ERROR":
                    status = "Fail: " + response.json()['authorizationCodes'][0]['statusMessage']
                else:
                    status = "Completed"
            except Exception as e:
                print(e)
                status = "Fail: " + "Response from cssm failed"
                logger.error(status, exc_info=True)
            s.update_status(slr_table_name, uuid, device_ip, status, "step2")
            try:
                logger.info(msg)
                logger.info(msg['authorizationCodes'][0])
                print(msg)
                logger.info(msg['authorizationCodes'][0]['authorizationCode'])
                final_msg = final_msg + msg['authorizationCodes'][0]['authorizationCode']
                print(final_msg)
            except Exception as e:
                print(e)
                s.update_authz_response_code(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, 'Error in getting response '
                                                                                           'from cssm')
                logger.error("Error in getting response from CSSM", exc_info=True)
            s.update_authz_response_code(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, final_msg)
        except Exception as e:
            logger.info("@@@@@ Printing Exception from main CSSM reserve license call...")
            print(e)
            logger.error('Error! Code: {c}, Message, {m}'.format(c=type(e).__name__, m=str(e)))
            # Following code is added to catch HTTP ConnectionError (Wrong URL etc)
            status = "Fail: " + str(type(e).__name__)
            s.update_authz_response_code(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, 'Error in getting response '
                                                                                       'from cssm')
            s.update_status(slr_table_name, uuid, device_ip, status, "step2")

        rows = s.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Started", "step2")
        rows_completed = s.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Completed", "step2")
        if (len(rows) == 0) and (len(rows_completed) != 0):
            # Updating the response status to Step 3 Complete
            response_update = {'status': "S3c"}
            TokensModel.update(uuid, response_update, "upload_info_store")

    @classmethod
    def slr_bulkDLC(cls, uuid, domain_name, dlcRequest, bearerToken):
        url = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/" + domain_name + \
              "/dlc_convert"
        headers = {
            "Authorization": "Bearer " + bearerToken,
            "Content-Type": "application/json"
        }

        if TokensModel.find_fileType(uuid) != "sl" and TokensModel.find_slr_type(uuid) == "slr":
            logger.info("Starting bulk dlc conversion for slr")
            dlcRequest_dict = {"virtualAccounts": []}
            for key, value in dlcRequest.items():
                dlcRequest_dict["virtualAccounts"].append({"dlcRequests": value, "name": key})
            logger.info("Before deleting device_ip from dlc_data_dict")
            logger.info(dlcRequest_dict)
            for item in dlcRequest_dict['virtualAccounts'][0]['dlcRequests']:
                item['sudi'].pop('device_ip')
            logger.info("After deleting device_ip from dlc_data_dict")
            logger.info(dlcRequest_dict)
            dlc_payload = json.dumps(dlcRequest_dict)
            logger.info(dlc_payload)
        if TokensModel.find_fileType(uuid) != "sl" and TokensModel.find_slr_type(uuid) == "slrx":
            logger.info("Starting bulk dlc conversion for slrx")
            logger.info("Before deleting device_ip from dlc_data_dict")
            logger.info(dlcRequest)
            for item in dlcRequest['virtualAccounts'][0]['dlcRequests']:
                item['sudi'].pop('device_ip')
            logger.info("After deleting device_ip from dlc_data_dict")
            logger.info(dlcRequest)
            dlc_payload = json.dumps(dlcRequest)
            logger.info(dlc_payload)
        try:
            for x in range(2):
                response = requests.request("POST", url, data=dlc_payload, headers=headers, timeout=10)
                try:
                    response = response.json()
                    for item in response["devices"]:
                        conversion_status = "dlc_" + item["conversionStatus"].lower()
                        udi_pid = item["sudi"]["udiPid"]
                        device_ip = TokensModel.find_device_ip(uuid,udi_pid)
                        if conversion_status != "dlc_in_progress":
                            TokensModel.insert_dlc_status(uuid, device_ip, conversion_status)
                        logger.info("**********DLC conversion status******")
                        logger.info(conversion_status)
                        if conversion_status == "dlc_convert_failed":
                            logger.info("DLC Failed")
                            logger.info(response)
                            break
                except Exception as e:
                    logger.error(e)
                    logger.error("Failed to parse DLC conversion response ")
                time.sleep(180)
        except Exception as e:
            logger.error(e)
            logger.error("DLC conversion request timed out")

    # Added for retries
    @classmethod
    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        giveup=lambda e: e.response is not None and e.response.status_code < 500
    )
    def send_post_with_retries(cls, url, data, headers, timeout):
        response = requests.request("POST", url, data=data, headers=headers, timeout=timeout)
        return response

