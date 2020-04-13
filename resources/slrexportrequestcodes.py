from flask_restful import Resource
import time
import datetime
from models.slr import slr
from models.tokens import TokensModel
from flask_jwt import jwt_required
from models.sl_logger import SlLogger
from resources.slrrequestcode import SlrRequestCode

logger = SlLogger.get_logger(__name__)


class Exportreqcodes(Resource):
    def __init__(self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del (self.slr)
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
            if update_row[0][5] != "S2c":
                # Changed to 200 from 400 on UI Dev team request
                logger.info("Request Codes are not yet generated for UUID: {}".format(uuid))
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
                logger.error("Status update operation upload_info_store failed!", exc_info=True)
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
                logger.info("lic_count_list:")
                logger.info(lic_count_list)
                logger.info("lic_ent_list:")
                logger.info(lic_ent_list)
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

                logger.info("==>> Printing devices from within get method for resource: Tokens <<==")
                logger.info(devices)
                logger.info("==>> Printing licenses from within get method for resource: Tokens <<==")
                logger.info(licenses)
                # Update individual device status based on ip addr row[1]
                # self.slr.update_status("slr_request_code_tbl", row[0], row[1], "Request Code Export Completed",
                #  "step1")

            # Now update 'upload_info_store' to S2cx
            response_update['status'] = "S2cx"
            try:
                TokensModel.update(uuid, response_update, "upload_info_store")
            except Exception as e:
                print(e)
                logger.error("Status update operation upload_info_store failed!", exc_info=True)
                return {'message': "Status update operation upload_info_store failed!", 'code': 500}

            try:
                registration_row = TokensModel.find_by_uuid(uuid, "upload_info_store")
            except Exception as e:
                print(e)
                logger.error("Data(UUID) search operation failed!", exc_info=True)
                return {"message": "Data(UUID) search operation failed!"}, 500

            try:
                domain_name, dlcRequest = SlrRequestCode.get_dlc_conversion_api_body(uuid)
                dlcRequest_dict = {"virtualAccounts": []}
                for key, value in dlcRequest.items():
                    dlcRequest_dict["virtualAccounts"].append({"dlcRequests": value, "name": key})
            except Exception as e:
                print(e)
                logger.error("Data(UUID) search operation failed!", exc_info=True)
                return {"message": "Data(UUID) search operation failed!"}, 500

            return {'registration-name': registration_row[0][2],
                    'slr-data-export-type': 'request_codes',
                    'registration-uuid': uuid,
                    'exported-on': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                    'total-devices': len(rows),
                    'devices-with-success': counter,
                    'devices': devices,
                    'dlcData': dlcRequest_dict}
        else:
            # Changed to 200 from 404 on UI Dev team request
            logger.info("Request with UUID: '{}' not found!".format(uuid))
            return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 200
