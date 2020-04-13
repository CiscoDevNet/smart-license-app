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
import config
from models.sl_logger import SlLogger

logger = SlLogger.get_logger(__name__)


class TokensModel:
    def __init__(self, uuid, ipaddr, username, password, sa_name, va_name, domain):
        self.uuid = uuid
        self.ipaddr = ipaddr
        self.username = username
        self.password = password
        self.sa_name = sa_name
        self.va_name = va_name
        self.domain = domain

    @classmethod
    def find_by_uuid(cls, uuid, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = ""

        if table == "device_store":
            query = "SELECT * FROM device_store WHERE uuid=?"
        elif table == "device_status_store":
            query = "SELECT * FROM device_status_store WHERE uuid=?"
        elif table == "validation_store":
            query = "SELECT * FROM validation_store WHERE uuid=?"
        elif table == "upload_info_store":
            query = "SELECT * FROM upload_info_store WHERE uuid=?"
        elif table == "slr_request_code_tbl":
            query = "SELECT * FROM slr_request_code_tbl WHERE uuid=?"

        result = cursor.execute(query, (uuid,))
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows from within classmethod: find_by_uuid <<==")
        logger.info(rows)
        return rows

    @classmethod
    def join_by_uuid(cls, uuid, table1, table2):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = ""

        if table1 == "slr_request_code_tbl" and table2 == "device_store":
            # query = "SELECT slr_request_code_tbl.uuid, slr_request_code_tbl.ipaddr," \
            #     " slr_request_code_tbl.step1, slr_request_code_tbl.step2, slr_request_code_tbl.step3," \
            #     " slr_request_code_tbl.authz_req_code, slr_request_code_tbl.license_count," \
            #     " slr_request_code_tbl.license_entitlement_tag, device_store.sa_name, device_store.va_name," \
            #     " device_store.domain, device_store.device_uuid FROM slr_request_code_tbl INNER JOIN device_store" \
            #     " ON slr_request_code_tbl.uuid = device_store.uuid WHERE slr_request_code_tbl.uuid=?"
            query = "SELECT slr_request_code_tbl.uuid, slr_request_code_tbl.ipaddr," \
                    " slr_request_code_tbl.step1, slr_request_code_tbl.step2, slr_request_code_tbl.step3," \
                    " slr_request_code_tbl.authz_req_code, slr_request_code_tbl.license_count," \
                    " slr_request_code_tbl.license_entitlement_tag, device_store.sa_name, device_store.va_name," \
                    " device_store.domain, device_store.device_uuid, slr_request_code_tbl.authz_response_code" \
                    " FROM slr_request_code_tbl INNER JOIN device_store" \
                    " ON slr_request_code_tbl.device_uuid = device_store.device_uuid WHERE slr_request_code_tbl.uuid=?"

        result = cursor.execute(query, (uuid,))
        # result = cursor.execute(query)
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows from within classmethod: join_by_uuid <<==")
        logger.info(rows)
        return rows

    @classmethod
    def find_by_uuid_column(cls, uuid, table, column):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = ""

        if table == "device_store":
            query = "SELECT " + column + " FROM device_store WHERE uuid=?"
        elif table == "device_status_store":
            query = "SELECT " + column + " FROM device_status_store WHERE uuid=?"
        elif table == "validation_store":
            query = "SELECT " + column + " FROM validation_store WHERE uuid=?"
        elif table == "upload_info_store":
            query = "SELECT " + column + " FROM upload_info_store WHERE uuid=?"

        result = cursor.execute(query, (uuid,))
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows from within classmethod: find_by_uuid_column <<==")
        logger.info(rows)
        return rows

    @classmethod
    def find_last_records(cls, user, table, order_column):
        # For debugging
        logger.info("In find_last_records ...")
        logger.info("user: {}".format(user))
        logger.info("table: {}".format(table))
        logger.info("order_column: {}".format(order_column))

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = ""

        if table == "upload_info_store":
            query = "SELECT * FROM upload_info_store" \
                    " LIMIT 10 OFFSET (SELECT COUNT(*) FROM upload_info_store)-10"

        result = cursor.execute(query, )
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows from within classmethod: find_last_records <<==")
        logger.info(rows)
        return rows

    @classmethod
    def find_by_uuid_and_column(cls, uuid, table, column, column_value):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = ""

        if table == "device_store":
            query = "SELECT * FROM device_store WHERE uuid=? AND " + column + "=?"
        elif table == "device_status_store":
            query = "SELECT * FROM device_status_store WHERE uuid=? AND " + column + "=?"
        elif table == "validation_store":
            query = "SELECT * FROM validation_store WHERE uuid=? AND " + column + "=?"
        elif table == "upload_info_store":
            query = "SELECT * FROM upload_info_store WHERE uuid=? AND " + column + "=?"

        result = cursor.execute(query, (uuid, column_value))
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows from within classmethod: find_by_uuid_and_column <<==")
        logger.info(rows)
        return rows

    @classmethod
    def find_by_uuid_distinct(cls, uuid, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT DISTINCT domain FROM ? WHERE uuid=?"
        result = cursor.execute(query, (table, uuid))
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows for unique domain names <<==")
        logger.info(rows)
        logger.info(rows[0][0])
        return rows

    @classmethod
    def find_by_uuid_slice(cls, uuid, page, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        offset = (page - 1) * 10
        logger.info("IN method find_by_uuid_slice...")
        logger.info("uuid is: {}".format(uuid))
        logger.info("page is: {}".format(page))
        logger.info("Posts per page / offset is: {}".format(config.POSTS_PER_PAGE))
        logger.info("Offset value is: {}".format(offset))

        if table == "device_store":
            query = "SELECT * FROM device_store WHERE uuid=? LIMIT ? OFFSET ?"
        elif table == "device_status_store":
            query = "SELECT * FROM device_status_store WHERE uuid=? LIMIT ? OFFSET ?"
        elif table == "validation_store":
            query = "SELECT * FROM validation_store WHERE uuid=? LIMIT ? OFFSET ?"
        elif table == "upload_info_store":
            query = "SELECT * FROM upload_info_store WHERE uuid=? LIMIT ? OFFSET ?"

        result = cursor.execute(query, (uuid, config.POSTS_PER_PAGE, offset))
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows for unique domain names <<==")
        logger.info(rows)
        return rows

    @classmethod
    def insert(cls, uuid, devices_data_list, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        # For debugging
        logger.info("In tokens model - insert method...")
        logger.info("devices_data_list: {}".format(devices_data_list))
        logger.info("uuid: {}".format(uuid))
        logger.info("table: {}".format(table))

        query = ""

        if table == "device_store":
            query = "INSERT INTO device_store VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            for device in devices_data_list:
                cursor.execute(query, (uuid, device['ipaddr'], device['username'], device['password'],
                                       device['sa_name'], device['va_name'], device['domain'], device['device_uuid'],
                                       "False"))
        elif table == "slr_request_code_tbl":
            query_slr = "INSERT INTO slr_request_code_tbl VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            logger.info("Starting data entry into device_store for SLR")
            for device in devices_data_list:
                cursor.execute(query_slr, (uuid, device['ipaddr'], "NS", "NS", "NS", "", "", device['license'],
                                           device['license_count'], device['tftp_server_ip'],
                                           device['tftp_server_path'], "", device['device_uuid']))
            logger.info("Executed data entry into device_store for SLR")
        elif table == "validation_store":
            query = "INSERT INTO validation_store VALUES (?, ?, ?, ?)"
            for device in devices_data_list:
                cursor.execute(query, (uuid, device['sa_name'], device['va_name'], device['domain']))
        elif table == "device_status_store":
            query = "INSERT INTO device_status_store VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            for device in devices_data_list:
                cursor.execute(query, (uuid, device['ipaddr'], device['username'], device['password'],
                                       device['sa_name'], device['va_name'], device['domain'], device['status'],
                                       device['device_uuid']))
        elif table == "upload_info_store":
            query = "INSERT INTO upload_info_store VALUES (?, ?, ?, ?, ?, ?)"

            for device in devices_data_list:
                cursor.execute(query, (uuid, device['userid'], device['filename'], device['type'], device['timestamp'],
                                       device['status']))
        connection.commit()
        connection.close()

    @classmethod
    def insert_slr(cls, uuid, devices_data_list, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        # For debugging
        logger.info("In tokens model - slr_insert method...")
        logger.info("devices_data_list: {}".format(devices_data_list))
        logger.info("uuid: {}".format(uuid))
        logger.info("table: {}".format(table))

        if table == "slr_request_code_tbl":
            query_slr = "INSERT INTO slr_request_code_tbl VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            logger.info("Starting insert data entry into slr_request_code_tbl for SLR")
            for device in devices_data_list:
                cursor.execute(query_slr, (uuid, device['ipaddr'], device['step1'], device['step2'], device['step3'],
                                           device['authz_req_code'], device['authz_response_code'], device['license'],
                                           device['license_count'], device['tftp_server_ip'],
                                           device['tftp_server_path'], device['license_entitlement_tag'],
                                           device['device_uuid']))
            logger.info("Executed insert data entry into slr_request_code_tbl for SLR")

        connection.commit()
        connection.close()

    @classmethod
    def update(cls, uuid, response, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        # query = ""
        logger.info("@@@@@@@@@@    In update method in models/tokens updating: {}".format(table))
        logger.info(response)
        logger.info(response['status'])
        logger.info("@@@@@@@@@@    In update method in models/tokens updated: {}".format(table))

        if table == "device_status_store":
            query = "UPDATE device_status_store SET status=? WHERE ipaddr=? AND uuid=?"
            cursor.execute(query, (response['status'], response['ipaddr'], uuid))
        elif table == "upload_info_store":
            query = "UPDATE upload_info_store SET status=? WHERE uuid=?"
            cursor.execute(query, (response['status'], uuid))
        connection.commit()
        connection.close()

    @classmethod
    def update_dlc(cls, uuid, dlc_flag):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "UPDATE device_store SET dlc_needed=? WHERE uuid=?"
        cursor.execute(query, (dlc_flag, uuid))
        connection.commit()
        connection.close()

    @classmethod
    def select_dlc(cls, uuid):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT dlc_needed from device_store WHERE uuid=?"
        result = cursor.execute(query, (uuid, ))
        row = result.fetchone()[0]
        connection.commit()
        connection.close()
        return row

    @classmethod
    def find_device_ip(cls, uuid, udi_pid):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT ipaddr from dlc_store WHERE uuid=? and udiPid=?"
        result = cursor.execute(query, (uuid,udi_pid,))
        device_ip = result.fetchone()[0]
        connection.commit()
        connection.close()
        return device_ip

    @classmethod
    def find_fileType(cls, uuid):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT type from upload_info_store WHERE uuid=?"
        result = cursor.execute(query, (uuid,))
        file_type = result.fetchone()[0]
        connection.commit()
        connection.close()
        return file_type

    @classmethod
    def find_slr_type(cls, uuid):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        slr_type = ''
        try:
            query = "SELECT slr_type from dlc_store WHERE uuid=?"
            result = cursor.execute(query, (uuid,))
            slr_type = result.fetchone()[0]
        except Exception as e:
            logger.error(e)
        connection.commit()
        connection.close()
        return slr_type

    @classmethod
    def insert_dlc_status(cls, uuid, ipaddr, status):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "INSERT INTO dlc_status_store VALUES (?, ?, ?)"
        cursor.execute(query, (uuid, ipaddr, status))
        connection.commit()
        connection.close()

    @classmethod
    def get_dlc_status(cls, uuid, ipaddr):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * from dlc_status_store WHERE uuid=? and ipaddr=?"
        result = cursor.execute(query, (uuid,ipaddr,))
        rows = result.fetchall()
        connection.close()
        logger.info("==>> Printing rows from within classmethod: get_dlc_status <<==")
        logger.info(rows)
        return rows

