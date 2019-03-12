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

import threading
from flask_restful import Resource
import time
from netmiko import ConnectHandler
from models.slr import slr
from models.tokens import TokensModel
import tftpy
import secrets
import config
import tempfile

accept = {"request": "accepted"}
slr_req_tbl = "slr_request_code_tbl"
database_err = {"message": "Data search operation failed!"}
s_start = "Started"
s_fail = "Fail: "
s_done = "Completed"
s_authc_fail = s_fail + "Authc fail"
step = "step3"
resp_status_started = "S4s"
resp_status_complete = "S4c"
extension = ".txt"
req_token_command = []
req_token_command.append("end")

if config.OS_TYPE == "windows":
    dest_dir = tempfile.gettempdir() + "\\"
else:
    dest_dir = "/tmp/"


class slrauthzswitch(Resource):
    def __init__ (self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del(self.slr)
        pass;

    def process_request(self, uuid):
        threads = []
        slr_table = slr_req_tbl
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e: 
            print(e)
            return database_err, 500
        for row in rows:
            response_update = {}
            response_update['status'] = resp_status_started
            TokensModel.update(uuid, response_update, "upload_info_store")
            self.slr.update_status(slr_table, row[0], row[1], s_start, step)
            print(row)
            val = self.slr.find_by_uuid_ipaddr(uuid, slr_table, row[1])
            print(val)
            if val[0][3] == s_done:
                th = threading.Thread(target=slrauthzswitch.send_authorize_information, args=(row[1], row[2], row[3], req_token_command, val[0][6], val[0][9], val[0][10], uuid))
                th.start()
                threads.append(th)
            else:
                self.slr.update_status(slr_table, uuid, row[1], "Error in previous step", step)
                rows = self.slr.find_by_step_status(slr_req_tbl, uuid, s_start, step)
                if (len(rows) == 0):
                    response_update = {}
                    response_update['status'] = resp_status_complete
                    TokensModel.update(uuid, response_update, "upload_info_store")
        return accept, 201

    @classmethod
    def send_authorize_information(cls, device_ip, username, password, cli, authz_info, tftp_server, tftp_loc, uuid):
        s = slr("", "", "")
        client = tftpy.TftpClient(tftp_server, 69)
        file_name =  device_ip + secrets.token_hex(5) + extension
        dest_file = dest_dir + file_name
        try:
            f = open(dest_file, "w+")
            print(authz_info)
            f.write(authz_info)
            f.close()
            client.upload(tftp_loc + file_name, dest_file)
            cli.append("lic smart reservation install file tftp://" + tftp_server + "/" + tftp_loc + file_name) 
            print(cli)
            slrauthzswitch.config_commands(device_ip, username, password, cli);
            s.update_status(slr_req_tbl, uuid, device_ip, s_done, step)
        except Exception as e:
            print(e)
            s.update_status(slr_req_tbl, uuid, device_ip, str(e).split(":")[0], step)

        rows = s.find_by_step_status(slr_req_tbl, uuid, s_start, step)
        if (len(rows) == 0):
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

    def get(self, uuid):
        return self.process_request(uuid)

    def post(self, uuid):
        return self.process_request(uuid)
