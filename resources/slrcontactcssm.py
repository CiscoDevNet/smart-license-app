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
import threading
from flask import json
from flask_restful import Resource, reqparse
from models.slr import slr
from models.tokens import TokensModel

accept = {"request": "accepted"}
slr_req_tbl = "slr_request_code_tbl"
database_err = {"message": "Data search operation failed!"}
s_start = "Started"
s_fail = "Fail: "
s_done = "Completed"
step = "step2"
resp_status_started = "S3s"
resp_status_complete = "S3c"
slr_table = slr_req_tbl
url_prefix = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/{}/virtual-accounts/{}" \
             "/reserve-licenses"
delim = " "


class slrcontactcssm(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def __init__ (self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del(self.slr)
        pass;

    def send_request_cssm(self, uuid, oauthToken):
        print("-------------------------------------------------------------------------------------------")
        print("contact cssm debugs")
        print("-------------------------------------------------------------------------------------------")
        threads = []
        slr_table = slr_req_tbl
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e: 
            print(e)
            return database_err, 500
        if not rows:
            return ({"request": "No Devices with this UUID"}), 400

        for row in rows:
            print("Launching threads to get auth tokens")
            response_update = {}
            response_update['status'] = resp_status_started
            TokensModel.update(uuid, response_update, "upload_info_store")
            self.slr.update_status(slr_table, row[0], row[1], s_start, step)
            th = threading.Thread(target=slrcontactcssm.get_cssm_response, args=(row[6], row[5], oauthToken, row[1], row[0]))
            th.start()
            threads.append(th)
        return (accept), 201
    
    @classmethod
    def get_cssm_response(cls, domain_name, va_name, oauthToken, device_ip, uuid):
        sl_token_dict = {}
        sl_token_dict['sl_token'] = ''
        sl_token_dict['error'] = ''
        final_msg = ""


        url = url_prefix.format(domain_name, va_name)
        print("Value of the rest api url is ")
        print(url)

        headers = {
            "Authorization": "Bearer " + oauthToken,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        payload = "{\"description\": \"SLR Token Automation\",\"expiresAfterDays\": 30,\"exportControlled\":" \
                  " \"Not Allowed\"}"
        s = slr("", "", "")
        try:
            i = 0
            status = s_done
            val = s.find_by_uuid_ipaddr(uuid, slr_table, device_ip)
            if val[0][2] != s_done:
                print(val[0][2])
                print(val)
                s.update_status(slr_table, uuid, device_ip, "Error in previous step", step)
                if (len(rows) == 0):
                    response_update = {}
                    response_update['status'] = resp_status_complete
                    TokensModel.update(uuid, response_update, "upload_info_store")
                del(s)
                return
            tags = val[0][11]
            first = 1
            licenses = []
            try:
                license_count = s.get_license_count(val[0]).split(delim);
                print(license_count)
                for tag in tags.split(delim):
                    try:
                        licenses.append({ "entitlementTag":tag, "quantity":license_count[i], "precedence":"LONGEST_TERM_FIRST"})
                    except Exception as e:
                        s.update_status(slr_table, uuid, device_ip, "License count and licenses are not set properly", step)
                        print(e)
                        rows = s.find_by_step_status(slr_req_tbl, uuid, s_start, step)
                        if (len(rows) == 0):
                            response_update = {}
                            response_update['status'] = resp_status_complete
                            TokensModel.update(uuid, response_update, "upload_info_store")
                        del(s)
                    i = i + 1
            except Exception as e:
                s.update_status(slr_table, uuid, device_ip, "License is not seperated by spaces", step)
                rows = s.find_by_step_status(slr_req_tbl, uuid, s_start, step)
                if (len(rows) == 0):
                    response_update = {}
                    response_update['status'] = resp_status_complete
                    TokensModel.update(uuid, response_update, "upload_info_store")
                return

            body = {"reservationRequests":[{ "reservationCode":val[0][5], "reservationType":"SPECIFIC", "licenses":licenses}]}
            print("Reservation request for uuid " + uuid + " for deive with ip " +  device_ip)
            print("-----------------------------------------------------------------------------")
            print(headers)
            print(body)
            print("-----------------------------------------------------------------------------")
            a = json.dumps(body)
            response = requests.request("POST", url, data=a, headers=headers, timeout=10)
            print(response.content.decode())
            if val[0][3] == s_done:
                print("Already marked step as completed, don't proceed further. This can happen when rest call takes time. It is more of a race condition, seen once in my testing. Handling for the same")
                return
            try:
                msg = response.json()
                print(msg['status'])
                if msg['status'] == "ERROR":
                    status = s_fail + response.json()['statusMessage']
                else:
                    status = s_done
            except Exception as e:
                print(e)
                status = s_fail + "Response from cssm failed"
            
            s.update_status(slr_table, uuid, device_ip, status, step)
            try:
                print(msg)
                print(msg['authorizationCodes'][0])
                if (1 == first) :
                    first = 0
                else:
                    final_msg = final_msg + delim
                print(msg['authorizationCodes'][0]['authorizationCode'])
                final_msg = final_msg + msg['authorizationCodes'][0]['authorizationCode'] 
            except Exception as e:
                print(e)
                s.update_authz_response_code(slr_req_tbl, uuid, device_ip, 'Error in getting response from cssm')
            s.update_authz_response_code(slr_req_tbl, uuid, device_ip, final_msg)
        except Exception as e:
            print(e)

        rows = s.find_by_step_status(slr_req_tbl, uuid, s_start, step)
        if (len(rows) == 0):
            response_update = {}
            response_update['status'] = resp_status_complete
            TokensModel.update(uuid, response_update, "upload_info_store")
        del(s)

    def get(self, uuid):
        data = slrcontactcssm.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])
        return self.send_request_cssm(uuid, data['oauth_token'])

    def post(self, uuid):
        data = slrcontactcssm.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])
        return self.send_request_cssm(uuid, data['oauth_token'])

