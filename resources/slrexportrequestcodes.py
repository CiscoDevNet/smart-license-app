from flask_restful import Resource
import time
import datetime
from models.slr import slr
from models.tokens import TokensModel


class Exportreqcodes(Resource):
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
            if update_row[0][5] != "S2c":
                # Changed to 200 from 400 on UI Dev team request
                return {"message": "Request Codes are not yet generated for UUID: {}".format(uuid)}, 200

        if rows:
            # Counter for devices with request code generated successfully
            counter = 0
            devices = []
            response_update = {}
            response_update['status'] = "S2sx"
            try:
                TokensModel.update(uuid, response_update, "upload_info_store")
            except Exception as e:
                print(e)
                return {'message': "Status update operation upload_info_store failed!", 'code': 500}

            for row in rows:
                licenses = []
                # Update individual device status based on ip addr row[1]
                # self.slr.update_status("slr_request_code_tbl", row[0], row[1], "Request Code Export Started", "step1")
                # Find out if for this device req code generation was successful
                if row[2] == "Completed":
                    counter += 1
                # license count and ent tag are passed as list
                lic_count_list = str(row[6]).split(" ")
                lic_ent_list = str(row[7]).split(" ")
                print("lic_count_list:")
                print(lic_count_list)
                print("lic_ent_list:")
                print(lic_ent_list)
                for element in range(len(lic_count_list)):
                    # First handle lic entitlement & count coming in as null string
                    lic_ent = lic_ent_list[element]
                    lic_count = lic_count_list[element]
                    if lic_ent == "":
                        lic_ent = "None"
                    if lic_count == "":
                        lic_count = "None"
                    licenses.append({'license-entitlement-tag': lic_ent, 'license-count': lic_count})
                # Handle request code coming in as null string
                request_code = row[5]
                if request_code == "":
                    request_code = "None"
                devices.append({'device-uuid': row[11], 'sa-name': row[8], 'va-name': row[9], 'domain': row[10],
                                'request-code': request_code, 'step1': row[2], 'licenses': licenses})

                print("==>> Printing devices from within get method for resource: Tokens <<==")
                print(devices)
                print("==>> Printing licenses from within get method for resource: Tokens <<==")
                print(licenses)
                # Update individual device status based on ip addr row[1]
                # self.slr.update_status("slr_request_code_tbl", row[0], row[1], "Request Code Export Completed",
                #  "step1")

            # Now update 'upload_info_store' to S2cx
            response_update['status'] = "S2cx"
            try:
                TokensModel.update(uuid, response_update, "upload_info_store")
            except Exception as e:
                print(e)
                return {'message': "Status update operation upload_info_store failed!", 'code': 500}

            try:
                registration_row = TokensModel.find_by_uuid(uuid, "upload_info_store")
            except Exception as e:
                print(e)
                return {"message": "Data(UUID) search operation failed!"}, 500

            return {'registration-name': registration_row[0][2],
                    'slr-data-export-type': 'request_codes',
                    'registration-uuid': uuid,
                    'exported-on': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    'total-devices': len(rows),
                    'devices-with-success': counter,
                    'devices': devices}
        else:
            # Changed to 200 from 404 on UI Dev team request
            return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 200
