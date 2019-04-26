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
from netmiko import ConnectHandler
import time
import threading
from models.slr import slr
from models.tokens import TokensModel

req_token_command = []
req_token_command.append("license smart reservation")
req_token_command.append("end")
req_token_command.append("license smart reservation request local")

req_udi_command = []
req_udi_command.append("end")
req_udi_command.append("sh license tech support | i Entitlement|Count")
entitlement_tag_string = "Entitlement tag"
count_string = "Count:"

slr_req_tbl = "slr_request_code_tbl"
slr_author_tbl = "slr_author_code_tbl"
database_err = {"message": "Data search operation failed!"}
s_start = "Started"
s_authc_fail = "Fail: Authc Fail"
s_prompt = "Fail: Status Prompt Missing"
s_done = "Completed"
s_map_not_found = "Mapping not found"
accept = {"request": "accepted"}
step = "step1"
resp_status_started = "S2s"
resp_status_complete = "S2c"
resp_status_failed = "S2f"
delim = " "


class slrrequestcode(Resource):
    def __init__ (self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del(self.slr)
        pass;

    def get(self, uuid):
        threads = []
        print(uuid)
        response = accept
        slr_table = slr_req_tbl
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e: 
            print(e)
            return database_err, 500

        for row in rows:
            print("Launching threads to get auth tokens")
            response_update = {}
            response_update['status'] = resp_status_started
            TokensModel.update(uuid, response_update, "upload_info_store")
            self.slr.update_status(slr_table, row[0], row[1], s_start, step)
            th = threading.Thread(target=slrrequestcode.execute_cli_wrapper, args=(row[1], row[2], row[3], req_token_command, row[0]))
            th.start()
            threads.append(th)
        return (response), 201

    @classmethod
    def execute_cli_wrapper(cls, device_ip, username, password, cli, uuid):
        print ("Value of username is "+ username + " password " + password)
        s = slr("", "", "")
        s.update_req_token(slr_req_tbl, uuid, device_ip, "")
        result = ""
        result_lic_count = ""
        try:
            lic_rows = s.find_by_uuid_ipaddr(uuid, slr_req_tbl, device_ip)
            license = s.get_license(lic_rows[0])
            if license is None: 
                output = slrrequestcode.config_commands(device_ip, username, password, cli)
                print("Value of the output is " + output)
                s.update_req_token(slr_req_tbl, uuid, device_ip, output.split('\n')[-2])
                output = slrrequestcode.config_commands(device_ip, username, password, req_udi_command)
                print(output)
                udi = (output.split('\n'))
                print("Value of udi is " + str(udi))
                first = 1
                first_count = 1
                # result = ""
                # result_lic_count = ""
                for entitlement_tag in udi:
                    print (entitlement_tag);
                    if entitlement_tag_string in entitlement_tag:
                        if first:
                            lic = entitlement_tag.split(":")[-1].replace(" ", "")
                            first = 0
                        else:
                            lic = entitlement_tag.split(":")[-1]
                        result = result + lic
                    if count_string in entitlement_tag:
                        if first_count:
                            lic_count_string = entitlement_tag.split(":")[-1].replace(" ", "")
                            first_count = 0
                        else:
                            lic_count_string = entitlement_tag.split(":")[-1]
                        result_lic_count = result_lic_count + lic_count_string
                print("Value of entitlement tag is " + result)
                print("Value of count of licenses is " + result_lic_count)
                # If we don't get lic ent tag and count from the device, indicate error
                if (result is "") or (result_lic_count is ""):
                    result = "LIC_ENT_TAG_NOT_FOUND"
                    result_lic_count = "LIC_COUNT_NOT_FOUND"
                s.update_entitlement_tag(slr_req_tbl, uuid, device_ip, result)
                s.update_license_count(slr_req_tbl, uuid, device_ip, result_lic_count)
            else:
                output = slrrequestcode.config_commands(device_ip, username, password, cli)
                print("Value of the output is " + output)
                s.update_req_token(slr_req_tbl, uuid, device_ip, output.split('\n')[-2])
                s.update_entitlement_tag(slr_req_tbl, uuid, device_ip, license)
            # If we don't get lic ent tag and count from the device, it is considered as failed
            if (result is "LIC_ENT_TAG_NOT_FOUND") or (result_lic_count is "LIC_COUNT_NOT_FOUND"):
                s.update_status(slr_req_tbl, uuid, device_ip, "License details not found from the device", step)
            else:
                s.update_status(slr_req_tbl, uuid, device_ip, s_done, step)
        except Exception as e:
            print(e)
            s.update_status(slr_req_tbl, uuid, device_ip, str(e).split(":")[0], step)
            # Added 04/16/19 - As export button and get auth key button is enabled eventhough
            # connection to device timed-out
            response_update = {}
            response_update['status'] = resp_status_failed
            TokensModel.update(uuid, response_update, "upload_info_store")

        rows = s.find_by_step_status(slr_req_tbl, uuid, s_start, step)
        rows_completed = s.find_by_step_status(slr_req_tbl, uuid, s_done, step)
        if (len(rows) == 0) and (len(rows_completed) != 0):
            response_update = {}
            response_update['status'] = resp_status_complete
            TokensModel.update(uuid, response_update, "upload_info_store")
        del(s)

    @classmethod
    def config_commands(cls, device_ip, username, password, command_list):
        device = {
            'device_type': 'cisco_xe',
            'ip': device_ip,
            'username': username,
            'password': password
        }

        # Give some time for Registration operation to be complete
        time.sleep(1)

        net_connect = ConnectHandler(**device)
        device_prompt = net_connect.find_prompt()

        print("++>> Starting CLI configuration process on device: ", device_prompt)
        if device_prompt:
            output = net_connect.send_config_set(command_list)
        else:
            print("Not able to get device prompt for ip address: ", device_ip)

        net_connect.disconnect()
        return output

