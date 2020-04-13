

from flask_restful import Resource
import time
import datetime
from models.slr import slr
from models.tokens import TokensModel
from flask_jwt import jwt_required
from models.sl_logger import SlLogger


logger = SlLogger.get_logger(__name__)


class Exportauthcodes(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del self.slr
        pass

    @jwt_required()
    def get(self, uuid):
        try:
            rows = TokensModel.join_by_uuid(uuid, "slr_request_code_tbl", "device_store")
            logger.info("Printing rows of devices. This should be one per device...")
            logger.info(rows)
        except Exception as e:
            print(e)
            logger.error("Data(UUID) search operation failed!", exc_info=True)
            return {"message": "Data(UUID) search operation failed!"}, 500

        try:
            update_row = TokensModel.find_by_uuid(uuid, "upload_info_store")
            logger.info("***** Printing row from upload_info_store...")
            logger.info(update_row)
            logger.info("***** Done printing row from upload_info_store.")
        except Exception as e:
            print(e)
            logger.error("Data(UUID) search operation failed!", exc_info=True)
            return {"message": "Data(UUID) search operation failed!"}, 500

        if update_row:
            if update_row[0][5] != "S3c":
                # Changed to 200 from 400 on UI Dev team request
                logger.info("Auth Codes are not yet generated for UUID: {}".format(uuid))
                return {"message": "Auth Codes are not yet generated for UUID: {}".format(uuid)}, 200

        if rows:
            # Counter for devices with auth code generated successfully
            counter = 0
            devices = []
            response_update = {}
            response_update['status'] = "S3sx"
            # This is a update status for all devices in a request
            try:
                TokensModel.update(uuid, response_update, "upload_info_store")
            except Exception as e:
                print(e)
                logger.error("Auth codes export status update operation upload_info_store failed!", exc_info=True)
                return {'message': "Auth codes export status update operation upload_info_store failed!", 'code': 500}

            for row in rows:
                # Update individual device status based on ip addr row[1]
                # self.slr.update_status("slr_request_code_tbl", row[0], row[1], "Auth Code Export Started", "step2")
                # Find out if for this device auth code generation was successful
                if row[3] == "Completed":
                    counter += 1
                # Handle auth_code coming in as null string
                auth_code = row[12]
                if auth_code == "":
                    auth_code = "None"
                devices.append({'device-uuid': row[11], 'auth-code': auth_code, 'step2': row[3]})
                logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
                logger.info(devices)
                # Update individual device status based on ip addr row[1]
                # self.slr.update_status("slr_request_code_tbl", row[0], row[1], "Auth Code Export Completed", "step2")

            # Now update 'upload_info_store' to S3cx
            response_update['status'] = "S3cx"
            try:
                TokensModel.update(uuid, response_update, "upload_info_store")
            except Exception as e:
                print(e)
                logger.error("Auth codes export status update operation upload_info_store failed!", exc_info=True)
                return {'message': "Auth codes export status update operation upload_info_store failed!", 'code': 500}

            try:
                registration_row = TokensModel.find_by_uuid(uuid, "upload_info_store")
            except Exception as e:
                print(e)
                logger.error("Data(UUID) search operation failed!", exc_info=True)
                return {"message": "Data(UUID) search operation failed!"}, 500

            return {'registration-name': registration_row[0][2],
                    'slr-data-export-type': 'auth_codes',
                    'registration-uuid': uuid,
                    'exported-on': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    'total-devices': len(rows),
                    'devices-with-success': counter,
                    'devices': devices}
        else:
            # Changed to 200 from 404 on UI Dev team request
            logger.error("Request with UUID: '{}' not found!".format(uuid), exc_info=True)
            return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 200
