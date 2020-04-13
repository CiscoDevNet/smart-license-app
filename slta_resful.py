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

from datetime import timedelta

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt import JWT
from resources.tokens import Tokens, TokensStatus, DeregisterTokens
from resources.cco_authen import UserCco
from resources.user import UserRegister
from resources.validate import Validate
from resources.registrations import Registrations
from resources.servereact import Servereact
from resources.servestaticfiles import Serveslcsv, Serveslrcsv, ServeFavicon
from resources.file import File, Fileuploadstatus
from create_tables import create_sql_tables
from resources.slrupdatestatus import SlrUpdateStatus
from resources.slrrequestcode import SlrRequestCode
from resources.slrrequestinfo import SlrRequestInfo
from resources.slrcontactcssm import SlrContactCSSM
from resources.slrauthswitch import SlrAuthSwitch
from resources.slrexportrequestcodes import Exportreqcodes
from resources.slrexportauthcodes import Exportauthcodes
from resources.slrimportcodes import ImportCodes
from resources.slrfetchauthcodesstatus import FetchAuthCodesStatus
from resources.resetPassword import ResetPassword
from resources.forgotPassword import ForgotPassword
from security import authenticate, identity
import platform
import config
from pathlib import Path
import yaml
from models.sl_logger import SlLogger

# Fetch App secret key from config.yaml
home = str(Path.home())

app = Flask(__name__, static_folder='frontend/build/static')

CORS(app)
app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=30)
logger = SlLogger.get_logger("netmiko")
logger = SlLogger.get_logger("paramiko.transport")


try:
    with open(home + "/config.yaml", 'r') as yamlfile:
        cfg = yaml.load(yamlfile)
        sec_key = cfg['secret_key']
except Exception:
    raise ("Secret Key not found!")

app.secret_key = sec_key
api = Api(app)

jwt = JWT(app, authenticate, identity)

# For frontend integration
api.add_resource(Servereact, '/', defaults={'path': ''})
api.add_resource(UserCco, '/authen')
api.add_resource(ResetPassword, '/resetPassword')
api.add_resource(ForgotPassword, '/forgotPassword')
api.add_resource(File, '/upload')
api.add_resource(Fileuploadstatus, '/devicesuploaded/<string:uuid>/<int:page>')
api.add_resource(Validate, '/sl/validate/<string:uuid>')
api.add_resource(Tokens, '/sl/tokens/<string:uuid>')
api.add_resource(DeregisterTokens, '/sl/tokens/deregister/<string:uuid>')
api.add_resource(TokensStatus, '/sl/tokens/status/<string:uuid>/<int:page>')
api.add_resource(UserRegister, '/register')
api.add_resource(Registrations, '/registrations')
api.add_resource(SlrUpdateStatus, '/slr/register/status/<string:uuid>/<int:page>')
api.add_resource(SlrRequestCode, '/slr/device/reqcode/<string:uuid>')
api.add_resource(Exportreqcodes, '/slr/exportreqcodes/<string:uuid>')
api.add_resource(Exportauthcodes, '/slr/exportauthcodes/<string:uuid>')
api.add_resource(ImportCodes, '/slr/importcodes')
api.add_resource(FetchAuthCodesStatus, '/slr/import/authcodes/status/<string:uuid>')
api.add_resource(SlrRequestInfo, '/registration/status/<string:uuid>')
api.add_resource(SlrContactCSSM, '/device/cssm/authkey/<string:uuid>')
api.add_resource(SlrAuthSwitch, '/slr/device/authkey/<string:uuid>')
api.add_resource(Serveslcsv, '/SampleDevicesDetails.csv')
api.add_resource(Serveslrcsv, '/SampleDevicesDetails-SLR.csv')
api.add_resource(ServeFavicon, '/favicon.ico')

if __name__ == '__main__':
    # first create tables
    create_sql_tables()
    # Fetch system info
    config.OS_TYPE = platform.system().lower()
    if config.OS_TYPE == "windows":
        app.run(debug=True, host='127.0.0.1', ssl_context='adhoc', use_reloader=True)
    else:
        app.run(debug=True, host='0.0.0.0', ssl_context='adhoc', use_reloader=True)
