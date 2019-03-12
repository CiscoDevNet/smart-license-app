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

import sqlite3
import requests
import threading
from flask_restful import Resource, reqparse
from subprocess import Popen, PIPE
import urllib3
import config
from math import ceil
import os
from distutils.version import StrictVersion
import time
from netmiko import ConnectHandler
from subprocess import call
from models.tokens import TokensModel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Tokens(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    # @jwt_required()
    def get(self, uuid):
        data = Tokens.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])
        try:
            rows = TokensModel.find_by_uuid(uuid, "device_store")
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

    def post(self, uuid):
        data = Tokens.parser.parse_args()
        try:
            rows = TokensModel.find_by_uuid_column(uuid, "device_store", "ipaddr")
            print('** NOW Printing rows for UUID:', rows)

        except:
            return {"message": "Data search operation failed!"}, 500

        if rows:
            try:
                print("Starting Token registration threads...")
                self.create_threads(rows, "registerToken", uuid, data['oauth_token'])
                response = {
                    'uuid': uuid,
                    'status': 'Tokens configuration process started!'
                }
                # Update SL Registration process as completed
                sl_status = {}
                sl_status['status'] = "slc"
                print("@@@@@@@@@@@ Now updating SL Status as completed @@@@@@@@@@@")
                TokensModel.update(uuid, sl_status, "upload_info_store")
                return response, 201
            except:
                {"message": "Tokens configuration process failed!"}, 500
        else:
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
        command = ['ping', param, '1', param_w, '1', ip]
        return call(command) == 0

    @classmethod
    def check_verison(cls, device_ip, username, password):
        # Check device version & platform type
        version_dict = {}
        version_dict['version'] = ''
        version_dict['error'] = ''

        url = "https://"+device_ip+":443/restconf/data/native/version"
        headers = {
                    'FOXY-API-VERSION': "1",
                    'Accept': "application/yang-data+json",
                    'Content-Type': "application/yang-data+json",
                    'Cache-Control': "no-cache"
        }

        try:
            response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False, timeout=5)
            print("Printing Device version info from GET call response...")
            print(response.content.decode())

            try:
                version = response.json()['Cisco-IOS-XE-native:version']
                version_dict['version'] = version
                print("====>>>>    Success: Got SW Version from the device   <<<<====\n\n")
                print("Version:", version)
            except:
                print('====>>>>    Unable to get SW Version from the device. Error:  %s' % response.text)
                version_dict['error'] = response.text
        except:
            print("==>> REST GET Call for check_version timed out!")
            version_dict['error'] = 'REST GET Call timed out'

        return version_dict

    @classmethod
    def check_pid(cls, device_ip, username, password):
        # Check device PID
        pid_dict = {}
        pid_dict['pid'] = ''
        pid_dict['error'] = ''

        url = "https://"+device_ip+":443/restconf/data/cisco-smart-license:licensing/state/state-info/udi/pid"

        headers = {
                    'FOXY-API-VERSION': "1",
                    'Accept': "application/yang-data+json",
                    'Content-Type': "application/yang-data+json",
                    'Cache-Control': "no-cache"
        }

        try:
            response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False, timeout=5)
            print("Printing device PID info from GET call response...")
            print(response.content.decode())

            try:
                pid = response.json()['cisco-smart-license:pid']
                pid_dict['pid'] = pid
                print("====>>>>    Success: Got PID from the device   <<<<====\n\n")
                print("PID:", pid)
            except:
                print('====>>>>    Unable to get PID from the device. Error:  %s' % response.text)
                pid_dict['error'] = response.text
        except:
            print("==>> REST GET Call for check_pid timed out!")
            pid_dict['error'] = 'REST GET Call timed out'

        return pid_dict

    @classmethod
    def check_device_type(cls, pid):
        # Initialize dict
        device_type_dict = {}
        device_type_dict['device_type'] = ""
        device_type_dict['exec_dlc'] = False
        switches = ["C9300-24U", "WS-C3850X-24U", "C3850-24P", "WS-C3850-24P"]
        routers = ["ISR4451-X/K9", "ISR4221/K9", "ISR4331/K9", "ISR4351/K9", "ISR4431/K9", "ISR4321/K9",
                   "ISR4461/K9", "ISRV", "CSR1000V"]

        # Check device type
        if pid in switches:
            device_type_dict['device_type'] = "switch"
        elif pid in routers:
            device_type_dict['device_type'] = "router"
        if ("3850-24P" or "3650" or "ISR" or "ASR" or "CSR") in pid:
            device_type_dict['exec_dlc'] = True
        return device_type_dict

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
            print("+++++++ DLC: Finding device prompt for: ", device_ip, " +++++++")
            device_prompt = net_connect.find_prompt()

            print("++>> Starting CLI execution process on device: ", device_prompt)
            if device_prompt:
                output = net_connect.send_command(cli)
            else:
                print("====>>>>    ERROR: Not able to get device prompt for ip address: ", device_ip, "    <<<<====")
        except:
            print("====>>>>    ERROR: NOT able to connect to the device: ", device_ip, "    <<<<====")
        # Close connection
        net_connect.disconnect()
        print("+++++++++ From method execute_cli returning output: ", output)
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

            print("++>> Starting CLI configuration process on device: ", device_prompt)
            if device_prompt:
                # output = net_connect.send_command("license smart conversion start")
                output = net_connect.send_config_set(command_list)
            else:
                print("Not able to get device prompt for ip address: ", device_ip)
        except:
            print("====>>>>    ERROR: NOT able to connect to the device: ", device_ip, "    <<<<====")
        # Close connection
        net_connect.disconnect()
        print("+++++++++ From method config_commands returning output: ", output)
        return output

    @classmethod
    def check_dlc(cls, device_output):
        print(" +++++++++ In method check_dlc ++++++++++")
        print(" +++++++++ Device output passed in: ", device_output)
        if device_output == "Smart Agent not registered":
            dlc_completed = False
        elif device_output == "":
            dlc_completed = True
        else:
            dlc_completed = True
        print(" +++++++++ From method check_dlc returning dlc_completed as: ", dlc_completed)
        return dlc_completed

    @classmethod
    def check_dlc_show(cls, show_output):
        print(" +++++++++ In method check_dlc_show ++++++++++")
        print(" +++++++++ Device show output passed in: ", show_output)
        if "Status: Already converted" in show_output:
            dlc_confirmed = True
        else:
            dlc_confirmed = False
        print(" +++++++++ From method check_dlc_show returning dlc_confirmed as: ", dlc_confirmed)
        return dlc_confirmed

    @classmethod
    def update_status(cls, uuid, device_ip):
        update = True
        status_row = TokensModel.find_by_uuid_and_column(uuid, "device_status_store", "ipaddr", device_ip)
        status = status_row[0][7]

        # Don't update status if DLC is executed as a last step else update status
        if (status == "Registered / DLC Executed") or (status == "Registered / DLC Execution Failed!") \
                or (status == "DLC Confirmation Failed!") or (status == "DLC Execution Failed!")\
                or (status == "CLI Execution Failed!"):
            print("+++++ Changing Value of update variable to: False")
            update = False
        else:
            print("+++++ Changing Value of update variable to: True")
            update = True
        return update

    @classmethod
    def getSLToken(cls, domain_name, va_name, oauthToken):
        sl_token_dict = {}
        sl_token_dict['sl_token'] = ''
        sl_token_dict['error'] = ''

        print("====>>>>    Acquire SL Token from CSSM    <<<<====\n\n")
        url = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/"\
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
                print("====>>>>    Success: Got SL Token from CSSM    <<<<====\n\n")
                print("SL Token:", sl_token+"\n\n")
                sl_token_dict['sl_token'] = sl_token
                sl_token_dict['error'] = "n/a"
            except:
                print('====>>>>    Unable to get SL Token from CSSM. Error:  %s' % response.text)
                sl_token_dict['error'] = response.text
                print('====>>>>    Creating SL Token from CSSM')
                sl_token_dict = Tokens.createSLToken(domain_name, va_name, oauthToken)
        except:
            print('====>>>>    Fetch SL Token from CSSM GET Request timed out!    <<<<====')
            sl_token_dict['error'] = "Fetch SL Token from CSSM GET Request timed out"
        return sl_token_dict

    @classmethod
    def createSLToken(cls, domain_name, va_name, oauthToken):
        sl_token_dict = {}
        sl_token_dict['sl_token'] = ''
        sl_token_dict['error'] = ''

        print("====>>>>    Create SL Token from CSSM    <<<<====\n\n")
        url = "https://apmx.cisco.com/services/api/smart-accounts-and-licensing/v1/accounts/"\
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
                print("====>>>>    Success: Created SL Token from CSSM    <<<<====\n\n")
                print("Newly created SL Token:", sl_token+"\n\n")
                sl_token_dict['sl_token'] = sl_token
                sl_token_dict['error'] = "n/a"
            except:
                print('====>>>>    Unable to get SL Token from CSSM. Error:  %s' % response.text)
                sl_token_dict['error'] = response.text
        except:
            print('====>>>>    Get SL Token from CSSM POST Request timed out!     <<<<====\n\n')
            sl_token_dict['error'] = 'Get SL Token from CSSM POST Request timed out'
        return sl_token_dict

    @classmethod
    def deregisterToken(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):
        return_code = None

        if Tokens.universal_ping(device_ip):
            print("====>>>>    De-registering Token from the Device: ", device_ip, "    <<<<====\n\n")
            url = "https://"+device_ip+":443/restconf/data/cisco-smart-license:de-register"
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
                print("Printing SL token de-register from the device POST call response...")
                print(response.content.decode())

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
                    print("====>>>>    Success: SL Token de-registered from the device: ", device_ip, "    <<<<====\n\n")
                except:
                    print("====>>>>    ERROR: Unable to De-register Token from the device: ",
                          device_ip, " Error:  %s" % response.text)
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
            except:
                print("SL token de-register from the device POST call timed out...")
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
            print("No connectivity to the device...")
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
        pid_str = None
        supported_device = False

        if Tokens.universal_ping(device_ip):
            try:
                # get device verison
                sw_version = Tokens.check_verison(device_ip, username, password)
                sw_ver_str = sw_version['version']
            except:
                print("====>>>>    ERROR: Unable to get SW Version!", device_ip)
                response = {
                    'ipaddr': device_ip,
                    'username': username,
                    'password': password,
                    'sa_name': sa,
                    'va_name': va,
                    'domain': domain,
                    'status': sw_version['error']
                }
                TokensModel.update(uuid, response, "device_status_store")

            try:
                # get device PID
                pid = Tokens.check_pid(device_ip, username, password)
                pid_str = pid['pid']
                device_type_dict = Tokens.check_device_type(pid_str)
            except:
                print("====>>>>    ERROR: Unable to get PID!", device_ip)
                response = {
                    'ipaddr': device_ip,
                    'username': username,
                    'password': password,
                    'sa_name': sa,
                    'va_name': va,
                    'domain': domain,
                    'status': pid['error']
                }
                TokensModel.update(uuid, response, "device_status_store")

            if sw_ver_str and pid_str:
                print("==>> sw_ver_str & device_type_dict['device_type']", sw_ver_str, device_type_dict['device_type'])
                if (StrictVersion(sw_ver_str) < StrictVersion("16.9")) and (device_type_dict['device_type'] == "switch"):
                    print("====>>>>    Unsupported switch type!", device_ip)
                    response = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': 'Unsupported Switch!'
                    }
                    TokensModel.update(uuid, response, "device_status_store")
                elif (StrictVersion(sw_ver_str) < StrictVersion("16.10")) and (device_type_dict['device_type'] == "router"):
                    print("====>>>>    Unsupported router type!", device_ip)
                    response = {
                        'ipaddr': device_ip,
                        'username': username,
                        'password': password,
                        'sa_name': sa,
                        'va_name': va,
                        'domain': domain,
                        'status': 'Unsupported Router!'
                    }
                    TokensModel.update(uuid, response, "device_status_store")
                else:
                    supported_device = True

                if supported_device:
                    try:
                        # get SL token first
                        sl_token = Tokens.getSLToken(domain, va, oauth_token)
                        sl_token_value = sl_token['sl_token']
                    except:
                        print("====>>>>    ERROR: Unable to get SL Token!", device_ip)
                        response = {
                            'ipaddr': device_ip,
                            'username': username,
                            'password': password,
                            'sa_name': sa,
                            'va_name': va,
                            'domain': domain,
                            'status': sl_token['error']
                        }
                        TokensModel.update(uuid, response, "device_status_store")
                    if sl_token_value:
                        print("====>>>>    Configuring SL Token on the Device: ", device_ip, "    <<<<====\n\n")
                        url = "https://"+device_ip+":443/restconf/data/cisco-smart-license:register-id-token"
                        payload = "{\"cisco-smart-license:register-id-token\": {\"id-token\" :\"" + sl_token_value + "\""" }}"
                        print("Printing Payload within registerToken...")
                        print(payload)
                        headers = {
                            'FOXY-API-VERSION': "1",
                            'Accept': "application/yang-data+json",
                            'Content-Type': "application/yang-data+json",
                            'Cache-Control': "no-cache"
                        }

                        try:
                            response = requests.request("POST", url, auth=(username, password), data=payload,
                                                        headers=headers, verify=False, timeout=5)
                            print("Printing SL token config on device POST call response...")
                            print(response.content.decode())
                            print("Printing SL token config on device POST call response...")

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
                                print("====>>>>    Success: SL Token configured on the device: ",
                                      device_ip, "    <<<<====\n\n")
                            except:
                                print("====>>>>    ERROR: Unable to configure SL Token on the device: ",
                                      device_ip, " Error:  %s" % response.text)
                                response_update = {
                                    'ipaddr': device_ip,
                                    'username': username,
                                    'password': password,
                                    'sa_name': sa,
                                    'va_name': va,
                                    'domain': domain,
                                    'status': 'Token config: Request Failed'
                                }
                                TokensModel.update(uuid, response_update, "device_status_store")
                        except:
                            print("==>> ERROR: SL token config on device POST call timed out...")
                            response_update = {
                                'ipaddr': device_ip,
                                'username': username,
                                'password': password,
                                'sa_name': sa,
                                'va_name': va,
                                'domain': domain,
                                'status': 'Token config: POST Request timed out'
                            }
                            TokensModel.update(uuid, response_update, "device_status_store")
                    # After token registration execute DLC
                    if device_type_dict['exec_dlc']:
                        dlc_completed = False
                        dlc_confirmed = False
                        dlc_successful = False
                        dlc_ctr = 0

                        while (not dlc_completed) and (dlc_ctr < 3):
                            time.sleep(2)
                            dlc_ctr += 1
                            print("++>> Executing DLC on Device: ", device_ip)
                            try:
                                device_output = Tokens.execute_cli(device_ip, username,
                                                                   password, "license smart conversion start")
                                show_output = Tokens.execute_cli(device_ip, username,
                                                                 password, "sh license status | sec License Conversion")
                                # Check DLC is successful or not
                                dlc_completed = Tokens.check_dlc(device_output)
                                if dlc_completed:
                                    # Verify DLC on the device
                                    dlc_confirmed = Tokens.check_dlc(show_output)
                                    if dlc_confirmed:
                                        dlc_successful = True
                                    else:
                                        print("TRY: ", dlc_ctr, "====>>>>    ERROR: Not able to confirm DLC on device: "
                                              , device_ip, "    <<<<====\n\n")
                                        response_update = {
                                            'ipaddr': device_ip,
                                            'username': username,
                                            'password': password,
                                            'sa_name': sa,
                                            'va_name': va,
                                            'domain': domain,
                                            'status': 'DLC Confirmation Failed!'
                                        }
                                        TokensModel.update(uuid, response_update, "device_status_store")
                                        dlc_successful = False
                                else:
                                    print("TRY: ", dlc_ctr, "====>>>>    ERROR: Not able to execute DLC: ",
                                          device_ip, "    <<<<====\n\n")
                                    response_update = {
                                        'ipaddr': device_ip,
                                        'username': username,
                                        'password': password,
                                        'sa_name': sa,
                                        'va_name': va,
                                        'domain': domain,
                                        'status': 'DLC Execution Failed!'
                                    }
                                    TokensModel.update(uuid, response_update, "device_status_store")
                                    dlc_successful = False
                            except:
                                print("TRY: ", dlc_ctr, "====>>>>    ERROR: Not able to execute CLI on: ", device_ip,
                                      "    <<<<====\n\n")
                                response_update = {
                                    'ipaddr': device_ip,
                                    'username': username,
                                    'password': password,
                                    'sa_name': sa,
                                    'va_name': va,
                                    'domain': domain,
                                    'status': 'CLI Execution Failed!'
                                }
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
                            print("++>> Done with DLC on Device: ", device_ip)
        else:
            print("No connectivity to the device...")
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
    def checkStatus(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):
        sl_token_value = ""

        if Tokens.universal_ping(device_ip):

            print("====>>>>    Checking registration status on the Device: ", device_ip, "    <<<<====\n\n")
            url = "https://"+device_ip+\
                  ":443/restconf/data/cisco-smart-license:licensing/state/state-info/registration/registration-state"
            headers = {
                'FOXY-API-VERSION': "1",
                'Accept': "application/yang-data+json",
                'Content-Type': "application/yang-data+json",
                'Cache-Control': "no-cache"
            }

            try:
                response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False, timeout=5)
                print("Printing registration status check from device GET call response...")
                print(response.content.decode())

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
                    print("+++++ UPDATE STATUS IS: ", Tokens.update_status(uuid, device_ip))
                    if Tokens.update_status(uuid, device_ip):
                        TokensModel.update(uuid, response_update, "device_status_store")
                    print("====>>>>    Success: Checked registration status on the device: ", device_ip,
                          "    <<<<====\n\n")
                except:
                    print("====>>>>    ERROR: Unable to check registration status!", device_ip)
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
            print("No connectivity to the device...")
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
        sl_token_value = ""

        if Tokens.universal_ping(device_ip):

            print("====>>>>    Checking registration status on the Device: ", device_ip, "    <<<<====\n\n")
            url = "https://"+device_ip+\
                  ":443/restconf/data/cisco-smart-license:licensing/state/state-info/registration/registration-state"
            headers = {
                'FOXY-API-VERSION': "1",
                'Accept': "application/yang-data+json",
                'Content-Type': "application/yang-data+json",
                'Cache-Control': "no-cache"
            }

            try:
                response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False, timeout=5)
                print("Printing registration status check from device GET call response...")
                print(response.content.decode())

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
                    print("+++++ UPDATE STATUS IS: ", Tokens.update_status(uuid, device_ip))
                    if Tokens.update_status(uuid, device_ip):
                        TokensModel.update(uuid, response_update, "device_status_store")
                    print("====>>>>    Success: Checked registration status on the device: ", device_ip,
                          "    <<<<====\n\n")
                except:
                    print("====>>>>    ERROR: Unable to check registration status!", device_ip)
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
            print("No connectivity to the device...")
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
        print("Entered create_threads method....")
        threads = []
        # Update SL Registration process as started
        sl_status = {}
        sl_status['status'] = "slc"
        print("@@@@@@@@@@@ Now updating SL Status as started/completed @@@@@@@@@@@")
        TokensModel.update(uuid, sl_status, "upload_info_store")

        try:
            for ip_addr_row in ip_addr_rows:
                print("Working on first IP addr: ", ip_addr_row[0])
                print("Calling proc TokensModel.find_by_uuid_and_columns....")
                va_domain_row = TokensModel.find_by_uuid_and_column(uuid, "device_store", "ipaddr", ip_addr_row[0])
                username = va_domain_row[0][2]
                password = va_domain_row[0][3]
                sa = va_domain_row[0][4]
                va = va_domain_row[0][5]
                domain = va_domain_row[0][6]
                print("Printing va & domain...")
                print(va)
                print(domain)

                if task == "registerToken":
                    print("Launching token registration threads!")
                    th = threading.Thread(target=Tokens.registerToken, args=(ip_addr_row[0], uuid, sa, va, domain,
                                                                             oauth_token, username, password))
                elif task == "checkStatus":
                    print("Launching registration status check threads!")
                    th = threading.Thread(target=Tokens.checkStatus, args=(ip_addr_row[0], uuid, sa, va, domain,
                                                                           oauth_token, username, password))
                elif task == "deregisterToken":
                    print("Launching token de-registration threads!")
                    th = threading.Thread(target=Tokens.deregisterToken, args=(ip_addr_row[0], uuid, sa, va, domain,
                                                                               oauth_token, username, password))
                th.start()
                threads.append(th)
            if task == "checkStatus":
                for thr in threads:
                    thr.join()
        except:
            print("Error in the threads!")

    def delete(self, uuid):
        data = Tokens.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])
        if not TokensModel.find_by_uuid(uuid, "device_store"):
            return {'message': "Request with UUID: '{}' doesn't exists.".format(uuid)}, 404

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM device_store WHERE uuid=?"
        cursor.execute(query, (uuid,))

        connection.commit()
        connection.close()

        return {'message': "Request with UUID: '{}' is deleted.".format(uuid)}


class DeregisterTokens(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('oauth_token',
                        type=str,
                        required=True,
                        help="This field cannot be blank."
                        )

    def post(self, uuid):
        data = Tokens.parser.parse_args()
        try:
            rows = TokensModel.find_by_uuid_column(uuid, "device_store", "ipaddr")

        except:
            return {"message": "Data search operation failed!"}, 500

        if rows:
            try:
                print("Starting Token de-registration threads...")
                Tokens.create_threads(rows, "deregisterToken", uuid, data['oauth_token'])
                response = {
                    'uuid': uuid,
                    'status': 'Tokens de-registration process started!'
                }
                return response, 201
            except:
                {"message": "Tokens de-registration process failed!"}, 500
        else:
            return {"message": "No devices found from request UUID!"}, 400


class TokensStatus(Resource):
    # @jwt_required()
    def post(self, uuid, page):
        data = Tokens.parser.parse_args()
        print("OAuth token is:", data['oauth_token'])
        sl_token = ""

        try:
            rows_uuid = TokensModel.find_by_uuid_column(uuid, "device_store", "ipaddr")
        except:
            return {"message": "Data search operation failed!"}, 500

        if rows_uuid:
            try:
                print("Starting registration status check threads...")
                Tokens.create_threads(rows_uuid, "checkStatus", uuid, data['oauth_token'])
            except:
                {"message": "Tokens status check process failed!"}, 500
        else:
            return {"message": "No devices found from request UUID!"}, 400

        config.NO_OF_DEVICES = len(rows_uuid)
        config.NO_OF_PAGES = ceil(config.NO_OF_DEVICES/10)
        print("Pagination: UUID for this request is:", uuid)
        print("Pagination: Total number of pages:", config.NO_OF_PAGES)
        print("Pagination: Page number requested is:", page)

        if page < 1 or page > config.NO_OF_PAGES:
            return {'message': "Page doesn't exists!"}, 400
        try:
            rows = TokensModel.find_by_uuid_slice(uuid, page, "device_status_store")
        except:
            return {"message": "Data search operation failed!"}, 500

        devices_status = []
        for row in rows:
            devices_status.append({'ipaddr': row[1], 'username': row[2], 'password': row[3], 'sa_name': row[4],
                                   'va_name': row[5], 'domain': row[6], 'status': row[7]})
        print("==>> Printing devices from within get method for resource: Tokens <<==")
        print(devices_status)
        if rows:
            return {'uuid': uuid,
                    'totalpages': config.NO_OF_PAGES,
                    'devices': devices_status}
        return {"message": "Request with UUID: '{}' not found while during Pagination!".format(uuid)}, 404
