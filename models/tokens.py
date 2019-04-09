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
        print("==>> Printing rows from within classmethod: find_by_uuid <<==")
        print(rows)
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
        print("==>> Printing rows from within classmethod: join_by_uuid <<==")
        print(rows)
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
        print("==>> Printing rows from within classmethod: find_by_uuid_column <<==")
        print(rows)
        return rows

    @classmethod
    def find_last_records(cls, user, table, order_column):
        # For debugging
        print("In find_last_records ...")
        print("user: ", user)
        print("table:", table)
        print("order_column:", order_column)

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = ""

        if table == "upload_info_store":
            query = "SELECT * FROM upload_info_store" \
                    " LIMIT 10 OFFSET (SELECT COUNT(*) FROM upload_info_store)-10"

        result = cursor.execute(query,)
        rows = result.fetchall()
        connection.close()
        print("==>> Printing rows from within classmethod: find_last_records <<==")
        print(rows)
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
        print("==>> Printing rows from within classmethod: find_by_uuid_and_column <<==")
        print(rows)
        return rows

    @classmethod
    def find_by_uuid_distinct(cls, uuid, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT DISTINCT domain FROM ? WHERE uuid=?"
        result = cursor.execute(query, (table, uuid))
        rows = result.fetchall()
        connection.close()
        print("==>> Printing rows for unique domain names <<==")
        print(rows)
        print(rows[0][0])
        return rows

    @classmethod
    def find_by_uuid_slice(cls, uuid, page, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        offset = (page - 1) * 10
        print("IN method find_by_uuid_slice...")
        print("uuid is:", uuid)
        print("page is:", page)
        print("Posts per page / offset is:", config.POSTS_PER_PAGE)
        print("Offset value is:", offset)

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
        print("==>> Printing rows for unique domain names <<==")
        print(rows)
        return rows

    @classmethod
    def insert(cls, uuid, devices_data_list, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        # For debugging
        print("In tokens model - insert method...")
        print("devices_data_list:", devices_data_list)
        print("uuid:", uuid)
        print("table:", table)

        query = ""

        if table == "device_store":
            query = "INSERT INTO device_store VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            for device in devices_data_list:
                cursor.execute(query, (uuid, device['ipaddr'], device['username'], device['password'],
                                       device['sa_name'], device['va_name'], device['domain'], device['device_uuid']))
        elif table == "slr_request_code_tbl":
            query_slr = "INSERT INTO slr_request_code_tbl VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            print("Starting data entry into device_store for SLR")
            for device in devices_data_list:
                cursor.execute(query_slr, (uuid, device['ipaddr'], "NS", "NS", "NS", "", "", device['license'],
                                           device['license_count'], device['tftp_server_ip'],
                                           device['tftp_server_path'], "", device['device_uuid']))
            print("Executed data entry into device_store for SLR")
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
        print("In tokens model - slr_insert method...")
        print("devices_data_list:", devices_data_list)
        print("uuid:", uuid)
        print("table:", table)

        query = ""

        if table == "slr_request_code_tbl":
            query_slr = "INSERT INTO slr_request_code_tbl VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            print("Starting insert data entry into slr_request_code_tbl for SLR")
            for device in devices_data_list:
                cursor.execute(query_slr, (uuid, device['ipaddr'], device['step1'], device['step2'], device['step3'],
                                           device['authz_req_code'], device['authz_response_code'], device['license'],
                                           device['license_count'], device['tftp_server_ip'],
                                           device['tftp_server_path'], device['license_entitlement_tag'],
                                           device['device_uuid']))
            print("Executed insert data entry into slr_request_code_tbl for SLR")

        connection.commit()
        connection.close()

    @classmethod
    def update(cls, uuid, response, table):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        # query = ""
        print("@@@@@@@@@@    In update method in models/tokens updating: ", table)
        print(response)
        print(response['status'])
        print("@@@@@@@@@@    In update method in models/tokens updated:", table)

        if table == "device_status_store":
            query = "UPDATE device_status_store SET status=? WHERE ipaddr=? AND uuid=?"
            cursor.execute(query, (response['status'], response['ipaddr'], uuid))
        elif table == "upload_info_store":
            query = "UPDATE upload_info_store SET status=? WHERE uuid=?"
            cursor.execute(query, (response['status'], uuid))

        connection.commit()
        connection.close()
