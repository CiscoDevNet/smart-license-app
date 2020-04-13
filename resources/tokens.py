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

import os
import sqlite3
import threading
import time
from distutils.version import StrictVersion
from math import ceil
from pathlib import Path
from subprocess import Popen, PIPE
from subprocess import call
import config
import requests
import urllib3
from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
from models.helper import Helper
from models.tokens import TokensModel
from netmiko import ConnectHandler
from models.sl_logger import SlLogger

home = str(Path.home())

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = SlLogger.get_logger(__name__)


class Tokens(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def get(self, uuid):
        data = Tokens.parser.parse_args()
        logger.info("OAuth token is: {}".format(data['oauth_token']))
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!", exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        devices = []
        for row in rows:
            devices.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                            'va_name': row[5], 'domain': row[6]})
        logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
        logger.info(devices)
        if rows:
            return {'uuid': uuid,
                    'devices': devices}
        logger.error("Request with UUID: '{}' not found!".format(uuid))
        return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404

    @jwt_required()
    def post(self, uuid):
        data = Tokens.parser.parse_args()
        try:
            rows = TokensModel.find_by_uuid_column(uuid, "device_store", "ipaddr")
            logger.info("** NOW Printing rows for UUID: {}".format(rows))
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!", exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        if rows:
            try:
                logger.info("Starting Token registration threads...")
                self.create_threads(rows, "registerToken", uuid, data['oauth_token'])
                response = {
                    'uuid': uuid,
                    'status': 'Tokens configuration process started!'
                }
                # Update SL Registration process as completed
                sl_status = {'status': "slc"}
                logger.info("@@@@@@@@@@@ Now updating SL Status as completed @@@@@@@@@@@")
                TokensModel.update(uuid, sl_status, "upload_info_store")
                logger.info(response)
                return response, 201
            except Exception as e:
                logger.error(e)
                logger.error("Tokens configuration process failed!", exc_info=True)
                {"message": "Tokens configuration process failed!"}, 500
        else:
            logger.error("No devices found from request UUID!", exc_info=True)
            return {"message": "No devices found from request UUID!"}, 400

    @classmethod
    def host_is_avail(cls, ip):
        cmd = ['ping', '-c', '1', '-t', '1', ip]
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        # code=0 means available
        return process.returncode == 0
        # return True

    @classmethod
    def check_ping(cls, ip):
        response = os.system("ping -c 1 " + ip)
        # and then check the response...
        return response == 0

    @classmethod
    def universal_ping(cls, ip):
        # ping command count option as a function of OS
        param = '-n' if config.OS_TYPE.lower() == 'windows' else '-c'
        param_w = '-w' if config.OS_TYPE.lower() == 'windows' else '-W'

        # Build command
        command = ['ping', param, '2', param_w, '1', ip]
        return call(command) == 0

    @classmethod
    def execute_cli(cls, device_ip, username, password, cli):
        output = ""
        device = {
            'device_type': 'cisco_xe',
            'ip': device_ip,
            'username': username,
            'password': password
        }

        # Give some time for Registration operation to be complete
        time.sleep(10)

        net_connect = ConnectHandler(**device)
        try:
            logger.info("+++++++ DLC: Finding device prompt for: {} +++++++".format(device_ip))
            device_prompt = net_connect.find_prompt()

            logger.info("++>> Starting CLI execution process on device: {}".format(device_prompt))
            if device_prompt:
                output = net_connect.send_command(cli)
            else:
                logger.error(
                    "====>>>>    ERROR: Not able to get device prompt for ip address: {} <<<<====".format(device_ip))
        except Exception as e:
            logger.error(e)
            logger.error("====>>>>    ERROR: NOT able to connect to the device: {} <<<<====".format(device_ip))
        # Close connection
        net_connect.disconnect()
        logger.info("+++++++++ From method execute_cli returning output: {}".format(output))
        return output

    @classmethod
    def config_commands(cls, device_ip, username, password, command_list):
        output = ""
        device = {
            'device_type': 'cisco_xe',
            'ip': device_ip,
            'username': username,
            'password': password
        }

        # Give some time for Registration operation to be complete
        time.sleep(1)

        net_connect = ConnectHandler(**device)
        try:
            device_prompt = net_connect.find_prompt()

            logger.info("++>> Starting CLI configuration process on device: {}".format(device_prompt))
            if device_prompt:
                # output = net_connect.send_command("license smart conversion start")
                output = net_connect.send_config_set(command_list)
            else:
                logger.error("Not able to get device prompt for ip address: {}".format(device_ip))
        except Exception as e:
            logger.error(e)
            logger.error("====>>>>    ERROR: NOT able to connect to the device: {}  <<<<====".format(device_ip))
        # Close connection
        net_connect.disconnect()
        logger.info("+++++++++ From method config_commands returning output: {}".format(output))
        return output

    @classmethod
    def check_dlc(cls, device_output):
        logger.info(" +++++++++ In method check_dlc ++++++++++")
        logger.info(" +++++++++ Device output passed in: {}".format(device_output))
        if device_output == "Smart Agent not registered":
            dlc_completed = False
        elif device_output == "":
            dlc_completed = True
        else:
            dlc_completed = True
        logger.info(" +++++++++ From method check_dlc returning dlc_completed as: {}".format(dlc_completed))
        return dlc_completed

    @classmethod
    def check_dlc_show(cls, show_output):
        logger.info(" +++++++++ In method check_dlc_show ++++++++++")
        logger.info(" +++++++++ Device show output passed in: {}".format(show_output))
        if "Status: Already converted" in show_output:
            dlc_confirmed = True
        else:
            dlc_confirmed = False
        logger.info(" +++++++++ From method check_dlc_show returning dlc_confirmed as: {}".format(dlc_confirmed))
        return dlc_confirmed

    @classmethod
    def update_status(cls, uuid, device_ip):
        update = True
        # status_row = TokensModel.find_by_uuid_and_column(uuid, "device_status_store", "ipaddr", device_ip)
        # status = status_row[0][7]

        # Don't update status if DLC is executed as a last step else update status
        # if (status == "Registered / DLC Executed") or (status == "Registered / DLC Execution Failed!") \
        #         or (status == "DLC Confirmation Failed!") or (status == "DLC Execution Failed!")\
        #         or (status == "CLI Execution Failed!"):
        if config.ERROR:
            logger.info("+++++ Changing Value of update variable to: False")
            update = False
        else:
            logger.info("+++++ Changing Value of update variable to: True")
            update = True
        return update

    @classmethod
    def getSLToken(cls, domain_name, va_name, oauthToken):
        sl_token_dict = {'sl_token': '', 'error': ''}

        logger.info("====>>>>    Acquire SL Token from CSSM    <<<<====\n\n")
        url = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/" \
              + domain_name + "/virtual-accounts/" + va_name + "/tokens"

        headers = {
            "Authorization": oauthToken,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

        try:
            response = requests.request("GET", url, headers=headers, timeout=5)
            # print(response.text)

            try:
                sl_token = response.json()['tokens'][0]['token']
                logger.info("====>>>>    Success: Got SL Token from CSSM    <<<<====\n\n")
                logger.info("SL Token: {}\n\n".format(sl_token))
                sl_token_dict['sl_token'] = sl_token
                sl_token_dict['error'] = "n/a"
            except Exception as e:
                logger.error(e)
                logger.error('====>>>>    Unable to get SL Token from CSSM. Error:  %s' % response.text)
                sl_token_dict['error'] = response.text
                logger.info('====>>>>    Creating SL Token from CSSM')
                sl_token_dict = Tokens.createSLToken(domain_name, va_name, oauthToken)
        except Exception as e:
            logger.error(e)
            logger.error('====>>>>    Fetch SL Token from CSSM GET Request timed out!    <<<<====')
            sl_token_dict['error'] = "Fetch SL Token from CSSM GET Request timed out"
        return sl_token_dict

    @classmethod
    def createSLToken(cls, domain_name, va_name, oauthToken):
        sl_token_dict = {'sl_token': '', 'error': ''}

        logger.info("====>>>>    Create SL Token from CSSM    <<<<====\n\n")
        url = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/" \
              + domain_name + "/virtual-accounts/" + va_name + "/tokens"
        payload = "{\"description\": \"SL Token Automation\",\"expiresAfterDays\": 30,\"exportControlled\":" \
                  " \"Not Allowed\"}"
        headers = {
            "Authorization": oauthToken,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

        try:
            response = requests.request("POST", url, data=payload, headers=headers, timeout=10)

            try:
                sl_token = response.json()['tokenInfo']['token']
                logger.info("====>>>>    Success: Created SL Token from CSSM    <<<<====\n\n")
                logger.info("Newly created SL Token: {} \n\n".format(sl_token))
                sl_token_dict['sl_token'] = sl_token
                sl_token_dict['error'] = "n/a"
            except Exception as e:
                logger.error(e)
                logger.error('====>>>>    Unable to get SL Token from CSSM. Error:  %s' % response.text)
                sl_token_dict['error'] = response.text
        except Exception as e:
            logger.error(e)
            logger.error('====>>>>    Get SL Token from CSSM POST Request timed out!     <<<<====\n\n')
            sl_token_dict['error'] = 'Get SL Token from CSSM POST Request timed out'
        return sl_token_dict

    @classmethod
    def deregisterToken(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):

        if Tokens.universal_ping(device_ip):
            logger.info("====>>>>    De-registering Token from the Device: {}  <<<<====\n\n".format(device_ip))
            url = "https://" + device_ip + ":443/restconf/data/cisco-smart-license:de-register"
            payload = ""
            headers = {
                'FOXY-API-VERSION': "1",
                'Accept': "application/yang-data+json",
                'Content-Type': "application/yang-data+json",
                'Cache-Control': "no-cache"
            }

            try:
                response = requests.request("POST", url, auth=(username, password), data=payload, headers=headers,
                                            verify=False, timeout=10)
                logger.info("Printing SL token de-register from the device POST call response...")
                logger.info(response.content.decode())

                try:
                    return_code = response.json()["cisco-smart-license:output"]["return-code"]
                    mapped_return_code = return_code
                    if return_code == "success":
                        mapped_return_code = "Unregistered"
                    else:
                        mapped_return_code = "De-register Failed!"
                    response_update = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': mapped_return_code
                    }
                    TokensModel.update(uuid, response_update, "device_status_store")
                    logger.info("====>>>>    Success: SL Token de-registered from the device: {} <<<<====\n\n".format(
                        device_ip))
                except Exception as e:
                    logger.error(e)
                    logger.error(
                        "====>>>>    ERROR: Unable to De-register Token from the device: {}<<<<====\n\n".format(
                            device_ip))
                response_update = {
                    'ipaddr': device_ip,
                    'username': username,
                    'password': password,
                    'sa_name': sa,
                    'va_name': va,
                    'domain': domain,
                    'status': 'Request Failed'
                }
                TokensModel.update(uuid, response_update, "device_status_store")
            except Exception as e:
                logger.error(e)
                logger.error("SL token de-register from the device POST call timed out...")
                response_update = {
                    'ipaddr': device_ip,
                    'username': username,
                    'password': password,
                    'sa_name': sa,
                    'va_name': va,
                    'domain': domain,
                    'status': 'Token De-register: POST Request timed out'
                }
                TokensModel.update(uuid, response_update, "device_status_store")
        else:
            logger.error("No connectivity to the device...")
            response_update = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': 'No Connectivity!'
            }
            TokensModel.update(uuid, response_update, "device_status_store")

    @classmethod
    def registerToken(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):
        sl_token_value = None
        sw_ver_str = None
        supported_device = False
        # device_type_dict = {}
        # device_type_dict['device_type'] = None
        # device_type_dict['exec_dlc'] = None
        # device_type_dict['error'] = None

        if Tokens.universal_ping(device_ip):

            config.ERROR, sw_ver_str, device_type_dict = Helper.check_dlc_required(device_ip, uuid, sa, va, domain,
                                                                                   oauth_token, username, password)
            # PID check for SL Connected part
            if not config.ERROR:
                if sw_ver_str and device_type_dict['device_type'] is not None:
                    logger.info("==>> sw_ver_str & device_type_dict['device_type']: {} & {}".format(sw_ver_str,
                                                                                                    device_type_dict[
                                                                                                        'device_type']))
                    if (StrictVersion(sw_ver_str) < StrictVersion("16.9")) and (
                            device_type_dict['device_type'] == "switch"):
                        logger.info("====>>>>    Unsupported switch type! {}".format(device_ip))
                        response = {
                            'ipaddr': device_ip,
                            'username': username,
                            'password': password,
                            'sa_name': sa,
                            'va_name': va,
                            'domain': domain,
                            'status': 'Unsupported Switch Version!'
                        }
                        config.ERROR = True
                        TokensModel.update(uuid, response, "device_status_store")
                    elif (StrictVersion(sw_ver_str) < StrictVersion("16.10")) and (
                            device_type_dict['device_type'] == "router"):
                        logger.info("====>>>>    Unsupported router type! {}".format(device_ip))
                        response = {
                            'ipaddr': device_ip,
                            'username': username,
                            'password': password,
                            'sa_name': sa,
                            'va_name': va,
                            'domain': domain,
                            'status': 'Unsupported Router Version!'
                        }
                        config.ERROR = True
                        TokensModel.update(uuid, response, "device_status_store")
                    else:
                        supported_device = True
                    # supported_device = True
                    if supported_device:
                        try:
                            # get SL token first
                            sl_token = Tokens.getSLToken(domain, va, oauth_token)
                            sl_token_value = sl_token['sl_token']
                        except Exception as e:
                            logger.error(e)
                            logger.error("====>>>>    ERROR: Unable to get SL Token! {}".format(device_ip))
                            response = {
                                'ipaddr': device_ip,
                                'username': username,
                                'password': password,
                                'sa_name': sa,
                                'va_name': va,
                                'domain': domain,
                                'status': sl_token['error']
                            }
                            config.ERROR = True
                            TokensModel.update(uuid, response, "device_status_store")
                        if sl_token_value:
                            logger.info(
                                "====>>>>    Configuring SL Token on the Device: {} <<<<====\n\n".format(device_ip))
                            url = "https://" + device_ip + ":443/restconf/data/cisco-smart-license:register-id-token"
                            payload = "{\"cisco-smart-license:register-id-token\": {\"id-token\" :\"" + \
                                      sl_token_value + "\""" }}"
                            logger.info("Printing Payload within registerToken...")
                            logger.info(payload)
                            headers = {
                                'FOXY-API-VERSION': "1",
                                'Accept': "application/yang-data+json",
                                'Content-Type': "application/yang-data+json",
                                'Cache-Control': "no-cache"
                            }

                            try:
                                response = requests.request("POST", url, auth=(username, password), data=payload,
                                                            headers=headers, verify=False, timeout=5)
                                logger.info("Printing SL token config on device POST call response...")
                                logger.info(response.content.decode())
                                logger.info("Printing SL token config on device POST call response...")

                                try:
                                    return_code = response.json()["cisco-smart-license:output"]["return-code"]
                                    mapped_return_code = return_code
                                    if return_code == "alreadyregistered":
                                        mapped_return_code = "Registered"
                                    elif return_code == "registrationinprogress":
                                        mapped_return_code = "InProgress"
                                    response_update = {
                                        'ipaddr': device_ip,
                                        'username': username,
                                        'password': password,
                                        'sa_name': sa,
                                        'va_name': va,
                                        'domain': domain,
                                        'status': mapped_return_code
                                    }
                                    TokensModel.update(uuid, response_update, "device_status_store")
                                    logger.info("====>>>>    Success: SL Token configured on the device: {} \
                                                <<<<====\n\n".format(device_ip))
                                except Exception as e:
                                    logger.error(e)
                                    logger.error("====>>>>    ERROR: Unable to configure SL Token on the device: {} \
                                                 Error: {}".format(device_ip, response.text))
                                    response_update = {
                                        'ipaddr': device_ip,
                                        'username': username,
                                        'password': password,
                                        'sa_name': sa,
                                        'va_name': va,
                                        'domain': domain,
                                        'status': 'Token config: Request Failed'
                                    }
                                    config.ERROR = True
                                    TokensModel.update(uuid, response_update, "device_status_store")
                            except Exception as e:
                                logger.error(e)
                                logger.error("==>> ERROR: SL token config on device POST call timed out...")
                                response_update = {
                                    'ipaddr': device_ip,
                                    'username': username,
                                    'password': password,
                                    'sa_name': sa,
                                    'va_name': va,
                                    'domain': domain,
                                    'status': 'Token config: POST Request timed out'
                                }
                                config.ERROR = True
                                TokensModel.update(uuid, response_update, "device_status_store")
                        # After token registration execute DLC
                        if TokensModel.select_dlc(uuid) == "True":
                            dlc_completed = False
                            dlc_confirmed = False
                            dlc_successful = False
                            dlc_ctr = 0

                            while (not dlc_completed) and (dlc_ctr < 3):
                                time.sleep(2)
                                dlc_ctr += 1
                                logger.info("++>> Executing DLC on Device: {}".format(device_ip))
                                try:
                                    device_output = Tokens.execute_cli(device_ip, username,
                                                                       password, "license smart conversion start")
                                    show_output = Tokens.execute_cli(device_ip, username,
                                                                     password,
                                                                     "sh license status | sec License Conversion")
                                    # Check DLC is successful or not
                                    dlc_completed = Tokens.check_dlc(device_output)
                                    if dlc_completed:
                                        # Verify DLC on the device
                                        dlc_confirmed = Tokens.check_dlc(show_output)
                                        if dlc_confirmed:
                                            dlc_successful = True
                                        else:
                                            logger.error("TRY: {} ====>>>> ERROR: Not able to confirm DLC on device: {} \
                                            <<<<====\n\n".format(dlc_ctr, device_ip))
                                            response_update = {
                                                'ipaddr': device_ip,
                                                'username': username,
                                                'password': password,
                                                'sa_name': sa,
                                                'va_name': va,
                                                'domain': domain,
                                                'status': 'DLC Confirmation Failed!'
                                            }
                                            config.ERROR = True
                                            TokensModel.update(uuid, response_update, "device_status_store")
                                            dlc_successful = False
                                    else:
                                        logger.error("TRY: {} ====>>>>    ERROR: Not able to execute DLC: {} \
                                        <<<<====\n\n".format(dlc_ctr, device_ip))
                                        response_update = {
                                            'ipaddr': device_ip,
                                            'username': username,
                                            'password': password,
                                            'sa_name': sa,
                                            'va_name': va,
                                            'domain': domain,
                                            'status': 'DLC Execution Failed!'
                                        }
                                        config.ERROR = True
                                        TokensModel.update(uuid, response_update, "device_status_store")
                                        dlc_successful = False
                                except Exception as e:
                                    logger.error(e)
                                    logger.error("TRY: {} ====>>>>    ERROR: Not able to execute CLI on: {} \
                                    <<<<====\n\n".format(dlc_ctr, device_ip))
                                    response_update = {
                                        'ipaddr': device_ip,
                                        'username': username,
                                        'password': password,
                                        'sa_name': sa,
                                        'va_name': va,
                                        'domain': domain,
                                        'status': 'CLI Execution Failed!'
                                    }
                                    config.ERROR = True
                                    TokensModel.update(uuid, response_update, "device_status_store")
                                    dlc_successful = False
                            if dlc_successful:
                                # DLC is executed successfully. Update status
                                response_update = {
                                    'ipaddr': device_ip,
                                    'username': username,
                                    'password': password,
                                    'sa_name': sa,
                                    'va_name': va,
                                    'domain': domain,
                                    'status': 'Registered / DLC Executed'
                                }
                                TokensModel.update(uuid, response_update, "device_status_store")
                                logger.info("++>> Done with DLC on Device: {} ".format(device_ip))
                else:
                    logger.info("==>> Unsupported Network Device type...")
                    response = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': 'Unsupported Device PID!'
                    }
                    config.ERROR = True
                    TokensModel.update(uuid, response, "device_status_store")
        else:
            logger.error("No connectivity to the device...")
            response_update = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': 'No Connectivity!'
            }
            config.ERROR = True
            TokensModel.update(uuid, response_update, "device_status_store")

    @classmethod
    def checkStatus(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):

        if Tokens.universal_ping(device_ip):

            logger.info("====>>>>    Checking registration status on the Device: {}<<<<====\n\n".format(device_ip))
            url = "https://" + device_ip + \
                  ":443/restconf/data/cisco-smart-license:licensing/state/state-info/registration/registration-state"
            headers = {
                'FOXY-API-VERSION': "1",
                'Accept': "application/yang-data+json",
                'Content-Type': "application/yang-data+json",
                'Cache-Control': "no-cache"
            }

            try:
                response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False,
                                            timeout=5)
                logger.info("Printing registration status check from device GET call response...")
                logger.info(response.content.decode())

                try:
                    return_code = response.json()["cisco-smart-license:registration-state"]
                    mapped_return_code = return_code
                    if return_code == "reg-state-not-registered":
                        mapped_return_code = "Unregistered"
                    elif return_code == "reg-state-failed":
                        mapped_return_code = "Failed"
                    elif return_code == "reg-state-complete":
                        mapped_return_code = "Registered"
                    elif return_code == "reg-state-in-progress":
                        mapped_return_code = "Inprogress"
                    elif return_code == "reg-state-retry":
                        mapped_return_code = "Inprogress"
                    response_update = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': mapped_return_code
                    }
                    logger.info("+++++ UPDATE STATUS IS: {}".format(Tokens.update_status(uuid, device_ip)))
                    if Tokens.update_status(uuid, device_ip):
                        TokensModel.update(uuid, response_update, "device_status_store")
                    logger.info("====>>>>    Success: Checked registration status on the device: {} \
                                <<<<====\n\n".format(device_ip))
                except Exception as e:
                    logger.error(e)
                    logger.error("====>>>>    ERROR: Unable to check registration status! {}".format(device_ip))
                    error_code = response.json()["errors"]["error"][0]["error-tag"]
                    response = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': error_code
                    }
                    TokensModel.update(uuid, response, "device_status_store")
            except requests.exceptions.ConnectionError:
                response_update = {
                    'ipaddr': device_ip,
                    'username': username,
                    'password': password,
                    'sa_name': sa,
                    'va_name': va,
                    'domain': domain,
                    'status': 'Connection Refused!'
                }
                TokensModel.update(uuid, response_update, "device_status_store")
        else:
            logger.error("No connectivity to the device...")
            response_update = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': 'No Connectivity!'
            }
            TokensModel.update(uuid, response_update, "device_status_store")

    # implement URI to check reg status from DB instead of the device
    @classmethod
    def checkStatusDB(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):

        if Tokens.universal_ping(device_ip):

            logger.info("====>>>>    Checking registration status on the Device: {} <<<<====\n\n".format(device_ip))
            url = "https://" + device_ip + \
                  ":443/restconf/data/cisco-smart-license:licensing/state/state-info/registration/registration-state"
            headers = {
                'FOXY-API-VERSION': "1",
                'Accept': "application/yang-data+json",
                'Content-Type': "application/yang-data+json",
                'Cache-Control': "no-cache"
            }

            try:
                response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False,
                                            timeout=5)
                logger.info("Printing registration status check from device GET call response...")
                logger.info(response.content.decode())

                try:
                    return_code = response.json()["cisco-smart-license:registration-state"]
                    mapped_return_code = return_code
                    if return_code == "reg-state-not-registered":
                        mapped_return_code = "Unregistered"
                    elif return_code == "reg-state-failed":
                        mapped_return_code = "Failed"
                    elif return_code == "reg-state-complete":
                        mapped_return_code = "Registered"
                    elif return_code == "reg-state-in-progress":
                        mapped_return_code = "Inprogress"
                    elif return_code == "reg-state-retry":
                        mapped_return_code = "Inprogress"
                    response_update = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': mapped_return_code
                    }
                    logger.info("+++++ UPDATE STATUS IS: {}".format(Tokens.update_status(uuid, device_ip)))
                    if Tokens.update_status(uuid, device_ip):
                        TokensModel.update(uuid, response_update, "device_status_store")
                    logger.info("====>>>>    Success: Checked registration status on the device: {} \
                                <<<<====\n\n".format(device_ip))
                except Exception as e:
                    logger.error(e)
                    logger.error("====>>>>    ERROR: Unable to check registration status! {}".format(device_ip))
                    error_code = response.json()["errors"]["error"][0]["error-tag"]
                    response = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': error_code
                    }
                    TokensModel.update(uuid, response, "device_status_store")
            except requests.exceptions.ConnectionError:
                response_update = {
                    'ipaddr': device_ip,
                    'username': username,
                    'password': password,
                    'sa_name': sa,
                    'va_name': va,
                    'domain': domain,
                    'status': 'Connection Refused!'
                }
                TokensModel.update(uuid, response_update, "device_status_store")
        else:
            logger.error("No connectivity to the device...")
            response_update = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': 'No Connectivity!'
            }
            TokensModel.update(uuid, response_update, "device_status_store")

    @classmethod
    def create_threads(cls, ip_addr_rows, task, uuid, oauth_token):
        logger.info("Entered create_threads method....")
        threads = []
        # Update SL Registration process as started
        sl_status = {'status': "slc"}
        logger.info("@@@@@@@@@@@ Now updating SL Status as started/completed @@@@@@@@@@@")
        TokensModel.update(uuid, sl_status, "upload_info_store")

        try:
            for ip_addr_row in ip_addr_rows:
                logger.info("Working on first IP addr: {}".format(ip_addr_row[0]))
                logger.info("Calling proc TokensModel.find_by_uuid_and_columns....")
                va_domain_row = TokensModel.find_by_uuid_and_column(uuid, "device_store", "ipaddr", ip_addr_row[0])
                username = va_domain_row[0][2]
                password = va_domain_row[0][3]
                sa = va_domain_row[0][4]
                va = va_domain_row[0][5]
                domain = va_domain_row[0][6]
                logger.info("Printing va & domain...")
                logger.info(va)
                logger.info(domain)

                if task == "registerToken":
                    logger.info("Launching token registration threads!")
                    th = threading.Thread(target=Tokens.registerToken, args=(ip_addr_row[0], uuid, sa, va, domain,
                                                                             oauth_token, username, password))
                elif task == "checkStatus":
                    logger.info("Launching registration status check threads!")
                    th = threading.Thread(target=Tokens.checkStatus, args=(ip_addr_row[0], uuid, sa, va, domain,
                                                                           oauth_token, username, password))
                elif task == "deregisterToken":
                    logger.info("Launching token de-registration threads!")
                    th = threading.Thread(target=Tokens.deregisterToken, args=(ip_addr_row[0], uuid, sa, va, domain,
                                                                               oauth_token, username, password))
                th.start()
                threads.append(th)
            if task == "checkStatus":
                for thr in threads:
                    thr.join()
        except Exception as e:
            logger.error(e)
            logger.error("Error in the threads!", exc_info=True)

    def delete(self, uuid):
        data = Tokens.parser.parse_args()
        logger.info("OAuth token is: {}".format(data['oauth_token']))
        if not TokensModel.find_by_uuid(uuid, "device_store"):
            logger.error("Request with UUID: '{}' doesn't exists.".format(uuid))
            return {'message': "Request with UUID: '{}' doesn't exists.".format(uuid)}, 404

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM device_store WHERE uuid=?"
        cursor.execute(query, (uuid,))

        connection.commit()
        connection.close()
        logger.info("Request with UUID: '{}' is deleted.".format(uuid))
        return {'message': "Request with UUID: '{}' is deleted.".format(uuid)}


class DeregisterTokens(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    @jwt_required()
    def post(self, uuid):
        data = Tokens.parser.parse_args()
        try:
            rows = TokensModel.find_by_uuid_column(uuid, "device_store", "ipaddr")

        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!", exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        if rows:
            try:
                logger.info("Starting Token de-registration threads...")
                Tokens.create_threads(rows, "deregisterToken", uuid, data['oauth_token'])
                response = {
                    'uuid': uuid,
                    'status': 'Tokens de-registration process started!'
                }
                logger.info(response)
                return response, 201
            except Exception as e:
                logger.error(e)
                logger.error("Tokens de-registration process failed!", exc_info=True)
                {"message": "Tokens de-registration process failed!"}, 500
        else:
            logger.error("No devices found from request UUID!", exc_info=True)
            return {"message": "No devices found from request UUID!"}, 400


class TokensStatus(Resource):
    @jwt_required()
    def post(self, uuid, page):
        data = Tokens.parser.parse_args()
        logger.info("OAuth token is: {}".format(data['oauth_token']))

        try:
            rows_uuid = TokensModel.find_by_uuid_column(uuid, "device_store", "ipaddr")
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!", exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        if rows_uuid:
            try:
                logger.info("Starting registration status check threads...")
                Tokens.create_threads(rows_uuid, "checkStatus", uuid, data['oauth_token'])
            except Exception as e:
                logger.error(e)
                logger.error("Tokens status check process failed!", exc_info=True)
                {"message": "Tokens status check process failed!"}, 500
        else:
            logger.error("No devices found from request UUID!")
            return {"message": "No devices found from request UUID!"}, 400

        config.NO_OF_DEVICES = len(rows_uuid)
        config.NO_OF_PAGES = ceil(config.NO_OF_DEVICES / 10)
        logger.info("Pagination: UUID for this request is: {}".format(uuid))
        logger.info("Pagination: Total number of pages: {}".format(config.NO_OF_PAGES))
        logger.info("Pagination: Page number requested is: {}".format(page))

        if page < 1 or page > config.NO_OF_PAGES:
            logger.error("Page doesn't exists!")
            return {'message': "Page doesn't exists!"}, 400
        try:
            rows = TokensModel.find_by_uuid_slice(uuid, page, "device_status_store")
        except Exception as e:
            logger.error(e)
            logger.error("Data search operation failed!", exc_info=True)
            return {"message": "Data search operation failed!"}, 500

        devices_status = []
        for row in rows:
            devices_status.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                                   'va_name': row[5], 'domain': row[6], 'status': row[7]})
        logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
        logger.info(devices_status)
        if rows:
            return {'uuid': uuid,
                    'totalpages': config.NO_OF_PAGES,
                    'devices': devices_status}
        logger.error("Request with UUID: '{}' not found while during Pagination!".format(uuid))
        return {"message": "Request with UUID: '{}' not found while during Pagination!".format(uuid)}, 404
