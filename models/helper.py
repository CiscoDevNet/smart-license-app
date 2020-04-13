import requests
import yaml
import json
import config
from pathlib import Path
from models.tokens import TokensModel
from models.sl_logger import SlLogger


home = str(Path.home())
logger = SlLogger.get_logger(__name__)


class Helper:

    @classmethod
    def check_pid(cls, device_ip, username, password):
        # Check device PID
        pid_dict = {'pid': None, 'error': ''}
        url = "https://" + device_ip + ":443/restconf/data/cisco-smart-license:licensing/state/state-info/udi/pid"

        headers = {
            'FOXY-API-VERSION': "1",
            'Accept': "application/yang-data+json",
            'Content-Type': "application/yang-data+json",
            'Cache-Control': "no-cache"
        }

        try:
            response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False, timeout=5)
            logger.info("Printing device PID info from GET call response...")
            logger.info(response.content.decode())

            try:
                pid = response.json()['cisco-smart-license:pid']
                pid_dict['pid'] = pid
                logger.info("====>>>>    Success: Got PID from the device   <<<<====\n\n")
                logger.info("PID: {}".format(pid))
            except Exception as e:
                logger.error(e)
                logger.error('====>>>>    Unable to get PID from the device. Error:  %s' % response.text, exc_info=True)
                pid_dict['error'] = response.text
        except Exception as e:
            logger.error(e)
            logger.error("==>> REST GET Call for check_pid timed out!", exc_info=True)
            pid_dict['error'] = 'REST GET Call timed out'

        return pid_dict

    @classmethod
    def check_version(cls, device_ip, username, password):
        # Check device version & platform type
        version_dict = {'version': None, 'error': ''}

        url = "https://" + device_ip + ":443/restconf/data/native/version"
        headers = {
            'FOXY-API-VERSION': "1",
            'Accept': "application/yang-data+json",
            'Content-Type': "application/yang-data+json",
            'Cache-Control': "no-cache"
        }

        try:
            response = requests.request("GET", url, auth=(username, password), headers=headers, verify=False, timeout=5)
            logger.info("Printing Device version info from GET call response...")
            logger.info(response.content.decode())

            try:
                version = response.json()['Cisco-IOS-XE-native:version']
                version_dict['version'] = version
                logger.info("====>>>>    Success: Got SW Version from the device   <<<<====\n\n")
                logger.info("Version: {}".format(version))
            except Exception as e:
                logger.error(e)
                logger.error('====>>>>    Unable to get SW Version from the device. Error:  %s' % response.text,
                             exec_info=True)
                version_dict['error'] = response.text
        except Exception as e:
            logger.error(e)
            logger.error("==>> REST GET Call for check_version timed out!", exc_info=True)
            version_dict['error'] = 'REST GET Call timed out'

        return version_dict

    @classmethod
    def check_device_type(cls, pid, uuid):
        # Initialize dict
        device_type_dict = {'device_type': None, 'error': None}
        logger.info("In method check_device_type....")
        logger.info(" ++++++++ device_type_dict DICT: {}".format(json.dumps(device_type_dict, indent=4)))
        logger.info(" ++++++++ DEVICE STRING: {}".format(device_type_dict['device_type']))
        try:
            with open(home + "/config.yaml", 'r') as yamlfile:
                cfg = yaml.load(yamlfile)
            routers = cfg['pids']['router_pids']
            switches = cfg['pids']['switch_pids']
            logger.info(" ++++++++ routers string: {}".format(routers))
            logger.info(" ++++++++ switches string: {}".format(switches))

            # Check device type
            if pid in switches:
                device_type_dict['device_type'] = "switch"
            elif pid in routers:
                device_type_dict['device_type'] = "router"

            if device_type_dict['device_type']:
                print("PID= "+pid)
                logger.info("====>>>>    Success: Got PID matched from config.yaml!   <<<<====\n\n")
                device_pids = ("ASR", "ISR", "CSR", "3850", "3650")
                if any(s in pid for s in device_pids):
                    print("PID found")
                    TokensModel.update_dlc(uuid, "True")
            logger.info(" ++++++++ device_type_dict DICT: {}".format(json.dumps(device_type_dict, indent=4)))
            logger.info(" ++++++++ DEVICE STRING: {}".format(device_type_dict['device_type']))
            logger.info("Leaving method check_device_type...")
            return device_type_dict
        except Exception:
            device_type_dict['error'] = 'PID not found! Check config.yaml file!'
            logger.error("PID not found! Check config.yaml file!")
            raise

        # switches = ["C9300-24U", "WS-C3850X-24U", "C3850-24P", "WS-C3850-24P"]
        # routers = ["ISR4451-X/K9", "ISR4221/K9", "ISR4331/K9", "ISR4351/K9", "ISR4431/K9", "ISR4321/K9",
        #            "ISR4461/K9", "ISRV", "CSR1000V"]
        #
        # # Check device type
        # if pid in switches:
        #     device_type_dict['device_type'] = "switch"
        # elif pid in routers:
        #     device_type_dict['device_type'] = "router"
        #
        # if device_type_dict['device_type']:
        #     if ("3850-24P" or "3650" or "ISR" or "ASR" or "CSR") in pid:
        #         device_type_dict['exec_dlc'] = True
        # return device_type_dict

    @classmethod
    def check_dlc_required(cls, device_ip, uuid, sa, va, domain, oauth_token, username, password):
        pid_str = None
        try:
            # get device verison
            sw_version = Helper.check_version(device_ip, username, password)
            sw_ver_str = sw_version['version']
            logger.info(" ++++++++ SW VERSION STRING: {}".format(sw_ver_str))
        except Exception as e:
            logger.error(e)
            logger.error("====>>>>    ERROR: Unable to fetch device SW Version! {}".format(device_ip))
            response = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': sw_version['error']
            }
            config.ERROR = True
            TokensModel.update(uuid, response, "device_status_store")

        try:
            # get device PID
            # Start here define empty PID dctionary in case we are not able to get thru check_pid method
            pid = Helper.check_pid(device_ip, username, password)
            pid_str = pid['pid']
            logger.info(" ++++++++ PID DICT: {}".format(json.dumps(pid, indent=4)))
            logger.info(" ++++++++ PID STRING: {}".format(pid_str))
            # device_type_dict = Tokens.check_device_type(pid_str)
        except Exception as e:
            logger.error(e)
            logger.error("====>>>>    ERROR: Unable to fetch device PID! {}".format(device_ip))
            response = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': pid['error']
            }
            config.ERROR = True
            TokensModel.update(uuid, response, "device_status_store")

        try:
            # check if PID is found and if it is belongs to a router or a switch
            device_type_dict = Helper.check_device_type(pid_str, uuid)
            logger.info(" ++++++++ device_type_dict DICT: {}".format(json.dumps(device_type_dict, indent=4)))
            logger.info(" ++++++++ DEVICE STRING: {}".format(device_type_dict['device_type']))
        except Exception as e:
            logger.error("====>>>>    ERROR: Unable to find PID! Check config.yaml file! {}".format(device_ip))
            logger.error('Error! Code: {c}, Message, {m}'.format(c=type(e).__name__, m=str(e)))
            status_str = "Unable to parse config.yaml file! Check file contents! ERROR: " + type(e).__name__ \
                         + " - " + str(e)
            response = {
                'ipaddr': device_ip,
                'username': username,
                'password': password,
                'sa_name': sa,
                'va_name': va,
                'domain': domain,
                'status': status_str
            }
            config.ERROR = True
            TokensModel.update(uuid, response, "device_status_store")
        return config.ERROR, sw_ver_str, device_type_dict
