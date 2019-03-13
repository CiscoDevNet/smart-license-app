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

from resources.tokens import Tokens, TokensStatus, DeregisterTokens
from resources.cco_authen import UserCco
from resources.validate import Validate
from resources.registrations import Registrations
from resources.servereact import Servereact
from resources.servestaticfiles import Serveslcsv, Serveslrcsv, ServeFavicon
from resources.file import File, Fileuploadstatus
from create_tables import create_sql_tables
from resources.slrgeneraterequestcode import slrgeneraterequestcode
from resources.slrrequestcode import slrrequestcode
from resources.slrrequestinfo import slrrequestinfo
from resources.slrcontactcssm import slrcontactcssm
from resources.slrauthzswitch import slrauthzswitch
import platform
import config

app = Flask(__name__, static_folder='frontend/build/static')
CORS(app)
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=30)
app.secret_key = 'slta'
api = Api(app)

# For frontend integration
api.add_resource(Servereact, '/', defaults={'path': ''})
api.add_resource(UserCco, '/authen')
api.add_resource(File, '/upload')
api.add_resource(Fileuploadstatus, '/devicesuploaded/<string:uuid>/<int:page>')
api.add_resource(Validate, '/sl/validate/<string:uuid>')
api.add_resource(Tokens, '/sl/tokens/<string:uuid>')
api.add_resource(DeregisterTokens, '/sl/tokens/deregister/<string:uuid>')
api.add_resource(TokensStatus, '/sl/tokens/status/<string:uuid>/<int:page>')
api.add_resource(Registrations, '/registrations')
api.add_resource(slrgeneraterequestcode, '/slr/register/status/<string:uuid>/<int:page>')
api.add_resource(slrrequestcode, '/slr/device/reqcode/<string:uuid>')
api.add_resource(slrrequestinfo, '/registration/status/<string:uuid>')
api.add_resource(slrcontactcssm, '/device/cssm/authkey/<string:uuid>')
api.add_resource(slrauthzswitch, '/slr/device/authkey/<string:uuid>')
api.add_resource(Serveslcsv, '/SampleDevicesDetails.csv')
api.add_resource(Serveslrcsv, '/SampleDevicesDetails-SLR.csv')
api.add_resource(ServeFavicon, '/favicon.ico')

if __name__ == '__main__':
    # first create tables
    create_sql_tables()
    # Fetch system info
    config.OS_TYPE = platform.system().lower()
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc', use_reloader=True)
