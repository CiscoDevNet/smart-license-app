from flask_restful import Resource
import time
import datetime
from models.slr import slr
from models.tokens import TokensModel


class Exportauthcodes(Resource):
    def __init__ (self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del(self.slr)
        pass

    # @jwt_required()
    def get(self, uuid):
        try:
            rows = TokensModel.join_by_uuid(uuid, "slr_request_code_tbl", "device_store")
            print("Printing rows of devices. This should be one per device...")
            print(rows)
        except Exception as e:
            print(e)
            return {"message": "Data(UUID) search operation failed!"}, 500

        try:
            update_row = TokensModel.find_by_uuid(uuid, "upload_info_store")
            print("***** Printing row from upload_info_store...")
            print(update_row)
            print("***** Done printing row from upload_info_store.")
        except Exception as e:
            print(e)
            return {"message": "Data(UUID) search operation failed!"}, 500

        if update_row:
            if update_row[0][5] != "S3c":
                # Changed to 200 from 400 on UI Dev team request
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
                print("==>> Printing devices from within get method for resource: Tokens <<==")
                print(devices)
                # Update individual device status based on ip addr row[1]
                # self.slr.update_status("slr_request_code_tbl", row[0], row[1], "Auth Code Export Completed", "step2")

            # Now update 'upload_info_store' to S3cx
            response_update['status'] = "S3cx"
            try:
                TokensModel.update(uuid, response_update, "upload_info_store")
            except Exception as e:
                print(e)
                return {'message': "Auth codes export status update operation upload_info_store failed!", 'code': 500}

            try:
                registration_row = TokensModel.find_by_uuid(uuid, "upload_info_store")
            except Exception as e:
                print(e)
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
            return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 200