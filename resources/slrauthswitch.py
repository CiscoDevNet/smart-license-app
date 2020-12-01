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
import json
import threading

import requests
from flask_restful import Resource
import time
from netmiko import ConnectHandler
from models.slr import slr
from models.tokens import TokensModel
import tftpy
import config
import tempfile
from flask_jwt import jwt_required
from models.sl_logger import SlLogger

# Constants
from resources.slrrequestcode import SlrRequestCode

SLR_REQUEST_CODE_TABLE_NAME = "slr_request_code_tbl"

if config.OS_TYPE == "windows":
    dest_dir = tempfile.gettempdir() + "\\"
else:
    dest_dir = "/tmp/"


logger = SlLogger.get_logger(__name__)


class SlrAuthSwitch(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del self.slr
        pass

    def process_request(self, uuid):
        threads = []
        slr_table = SLR_REQUEST_CODE_TABLE_NAME
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e:
            print(e)
            logger.error({"message": "Data search operation failed!"}, exc_info=True)
            return {"message": "Data search operation failed!"}, 500
        for row in rows:
            # Updating the response status to Step 4 started
            response_update = {'status': "S4s"}
            TokensModel.update(uuid, response_update, "upload_info_store")
            self.slr.update_status(slr_table, row[0], row[1], "Started", "step3")
            logger.info(row)
            val = self.slr.find_by_uuid_ipaddr(uuid, slr_table, row[1])
            logger.info(val)
            if val[0][3] == "Completed":
                th = threading.Thread(target=SlrAuthSwitch.send_authorize_information, args=(row[1], row[2], row[3],
                                                                                             ["end"], val[0][6],
                                                                                             val[0][9], val[0][10],
                                                                                             uuid))
                th.start()
                threads.append(th)
            else:
                self.slr.update_status(slr_table, uuid, row[1], "Error in previous step", "step3")
                rows = self.slr.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Started", "step3")
                if len(rows) == 0:
                    # Updating the response status to Step 4 completed
                    response_update = {'status': "S4c"}
                    TokensModel.update(uuid, response_update, "upload_info_store")
        logger.info({"request": "accepted"})
        return {"request": "accepted"}, 201

    @classmethod
    def send_authorize_information(cls, device_ip, username, password, cli, authz_info, tftp_server, tftp_loc, uuid):
        s = slr("", "", "")
        try:
            logger.info("Trying to connect to tftp server:{}".format(tftp_server))
            client = tftpy.TftpClient(tftp_server, 69)
            file_name = device_ip + ".txt"
            dest_file = dest_dir + file_name
            try:
                f = open(dest_file, "w+")
                logger.info(authz_info)
                f.write(authz_info)
                f.close()
                logger.info("Trying to upload file:{}".format(file_name))
                client.upload(file_name, dest_file)
                cli.append("lic smart reservation install file tftp://" + tftp_server + "/" + file_name)
                logger.info(cli)
                SlrAuthSwitch.config_commands(device_ip, username, password, cli)
                #if dlc_status_rows is not empty means dlc is performed
                dlc_status_rows = TokensModel.get_dlc_status(uuid, device_ip)
                if dlc_status_rows:
                    dlc_status = dlc_status_rows[0][2]
                    if dlc_status == "dlc_convert_success":
                        s.update_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, "DLC Success and Completed", "step3")
                    else:
                        s.update_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, "DLC Failed and SLR Successful",
                                        "step3")
                else:
                    s.update_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, "Completed", "step3")
            except Exception as e:
                print("file upload failed:", e)
                logger.info("Failed uploading file:{}".format(file_name))
                s.update_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, device_ip, str(e).split(":")[0], "step3")
        except Exception as e:
            logger.info("Failure connecting to tftp server:{}".format(tftp_server))
            print("Connection to tftp server failed:", e)

        rows = s.find_by_step_status(SLR_REQUEST_CODE_TABLE_NAME, uuid, "Started", "step3")
        if len(rows) == 0:
            # Updating the response status to Step 4 completed
            response_update = {'status': "S4c"}
            TokensModel.update(uuid, response_update, "upload_info_store")
        del s

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

        logger.info("++>> Starting CLI configuration process on device: {}".format(device_prompt))
        if device_prompt:
            output = net_connect.send_config_set(command_list)
        else:
            logger.error("Not able to get device prompt for ip address: {}".format(device_ip))

        net_connect.disconnect()
        return output

    @jwt_required()
    def post(self, uuid):
        return self.process_request(uuid)
