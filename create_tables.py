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

slr_request_code_tbl = "CREATE TABLE IF NOT EXISTS slr_request_code_tbl (uuid text, ipaddr text, step1 text," \
                       " step2 text, step3 text, authz_req_code text, authz_response_code text, license text," \
                       " license_count text, tftp_server_ip text, tftp_server_path text," \
                       " license_entitlement_tag text, device_uuid text)"


def create_sql_tables():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()

    create_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username text, password text)"
    cursor.execute(create_table)

    create_table = "CREATE TABLE IF NOT EXISTS device_store (uuid text, ipaddr text, username text," \
                   " password text, sa_name text, va_name text, domain text, device_uuid text)"
    cursor.execute(create_table)

    create_table = "CREATE TABLE IF NOT EXISTS validation_store (uuid text, sa_name text, va_name text, domain text)"
    cursor.execute(create_table)

    # including more fields to device_status_store
    create_table = "CREATE TABLE IF NOT EXISTS device_status_store (uuid text, ipaddr text," \
                   " username text, password text, sa_name text, va_name text, domain text, status text," \
                   " device_uuid text)"
    cursor.execute(create_table)

    create_table = "CREATE TABLE IF NOT EXISTS upload_info_store (uuid text, userid text, filename text, type text," \
                   " timestamp text, status text)"
    cursor.execute(create_table)
    cursor.execute(slr_request_code_tbl)

    connection.commit()
    connection.close()
