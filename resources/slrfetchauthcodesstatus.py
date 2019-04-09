from flask_restful import Resource
import time
import datetime
from models.slr import slr
from models.tokens import TokensModel


class Fetchauthcodesstatus(Resource):
    def __init__ (self):
        self.slr = slr("", "", "")
        pass

    def __del__(self):
        del(self.slr)
        pass

    # @jwt_required()
    def get(self, uuid):
        try:
            rows = TokensModel.find_by_uuid(uuid, "slr_request_code_tbl")
        except:
            return {"message": "Data search operation failed!"}, 500

        if rows:
            # Counter for total no of devices for which auth codes needs to be generated
            total_devices = len(rows)
            not_started_counter = 0
            started_counter = 0
            failed_counter = 0
            processed_counter = 0
            # Updated for all status types
            for row in rows:
                if row[3] == "NS":
                    not_started_counter += 1
                elif row[3] == "Started":
                    started_counter += 1
                elif row[3] == "Completed":
                    processed_counter += 1
                elif "Error" in row[3]:
                    failed_counter += 1
                    processed_counter += 1
            if processed_counter == total_devices:
                status = "Completed"
            elif not_started_counter == total_devices:
                status = "NotStarted"
            else:
                status = "In-Progress"
            return {'message': 'Sucessfully fetched status of Auth Codes!',
                    'progress': status,
                    'total': total_devices,
                    'failed': failed_counter,
                    'processed': processed_counter}, 200
        else:
            return {"message": "Request with UUID: '{}' not found!".format(uuid)}, 404