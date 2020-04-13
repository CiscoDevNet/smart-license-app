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

import config
from models.databasehandler import databasehandler
from models.sl_logger import SlLogger

slr_debug = 1

logger = SlLogger.get_logger(__name__)


class slr:
    def __init__(self, uuid, authz_code, status):
        self.uuid = uuid
        self.authz_code = authz_code
        self.status = status
        self.db = databasehandler()

    def find_by_uuid(self, uuid, table, column="*"):
        logger.info("**** Start: In SLR models - find_by_uuid ****")
        rows = self.db.query("select " + column + " from \"" + table + "\" where uuid = \"" + uuid + "\"")
        if slr_debug:
            logger.info(rows)
        logger.info("**** Done: In SLR models - find_by_uuid ****")
        return rows

    def find_by_uuid_ipaddr(self, uuid, table, ip_addr, column="*"):
        logger.info("**** Start: In SLR models - find_by_uuid_ipaddr ****")
        rows = self.db.query(
            "select " + column + " from \"" + table + "\" where uuid = \"" + uuid + "\" and ipaddr = \"" + ip_addr +
            "\"")
        if slr_debug:
            logger.info(rows)
        logger.info("**** Done: In SLR models - find_by_uuid_ipaddr ****")
        return rows

    def find_by_uuid_slice(self, uuid, table, page, column="*"):
        logger.info("**** Start: In SLR models - find_by_uuid_slice ****")
        rows = self.db.query(
            "select " + column + " from \"" + table + "\" where uuid = \"" + uuid + "\"" + " LIMIT " + str(
                config.POSTS_PER_PAGE) + " OFFSET " + str(page))
        if slr_debug:
            logger.info("select " + column + " from \"" + table + "\" where uuid = \"" + uuid + "\"" + " LIMIT " + str(
                config.POSTS_PER_PAGE) + " OFFSET " + str(page))
            logger.info(rows)
        logger.info("**** Done: In SLR models - find_by_uuid_slice ****")
        return rows

    def update_status(self, table, uuid, ip_addr, status, step):
        logger.info("**** Start: In SLR models - update_status ****")
        self.db.query(
            "update " + table + " set " + step + "=\"" + status + "\" where uuid=\"" + uuid + "\" and ipaddr =\"" +
            ip_addr + "\"")
        if slr_debug:
            logger.info(
                "update " + table + " set " + step + "=\"" + status + "\" where uuid=\"" + uuid + "\" and ipaddr =\""
                + ip_addr + "\"")
        logger.info("**** Done: In SLR models - update_status ****")

    def update_status_device_uuid(self, table, uuid, device_uuid, status, step):
        logger.info(
            "**** Start: In SLR models - update_status_device_uuid based on device_uuid (Import Auth Codes)****")
        self.db.query(
            "update " + table + " set " + step + "=\"" + status + "\" where uuid=\"" + uuid + "\" and device_uuid "
                                                                                              "=\"" + device_uuid +
            "\"")
        if slr_debug:
            logger.info(
                "update " + table + " set " + step + "=\"" + status + "\" where uuid=\"" + uuid + "\" and device_uuid "
                                                                                                  "=\"" + device_uuid
                + "\"")
        logger.info("**** Done: In SLR models - update_status_device_uuid ****")

    def update_req_token(self, table, uuid, ip_addr, req_token):
        logger.info("**** Start: In SLR models - update_req_token ****")
        self.db.query(
            "update " + table + " set authz_req_code=\"" + req_token + "\" where uuid=\"" + uuid + "\" and ipaddr "
                                                                                                   "=\"" + ip_addr +
            "\"")
        if slr_debug:
            logger.info(
                "update " + table + " set authz_req_code=\"" + req_token + "\" where uuid=\"" + uuid + "\" and "
                                                                                                       "ipaddr =\""
                + ip_addr + "\"")
        logger.info("**** Done: In SLR models - update_req_token ****")

    def update_authz_response_code(self, table, uuid, ip_addr, req_token):
        logger.info("**** Start: In SLR models - update_authz_response_code ****")
        self.db.query(
            "update " + table + " set authz_response_code=\"" + req_token + "\" where uuid=\"" + uuid + "\" and  "
                                                                                                        "ipaddr =\""
            + ip_addr + "\"")
        if slr_debug:
            logger.info(
                "update " + table + " set authz_response_code=\"" + req_token + "\" where uuid=\"" + uuid + "\" and "
                                                                                                            "ipaddr "
                                                                                                            "=\"" +
                ip_addr + "\"")
        logger.info("**** Done: In SLR models - update_authz_response_code ****")

    def update_authz_response_code_device_uuid(self, table, uuid, device_uuid, req_token):
        logger.info(
            "Start: In SLR models - update_authz_response_code_device_uuid based on device_uuid (Import Auth Codes)")
        self.db.query(
            "update " + table + " set authz_response_code=\"" + req_token + "\" where uuid=\"" + uuid + "\" and "
                                                                                                        "device_uuid "
                                                                                                        "=\"" +
            device_uuid + "\"")
        if slr_debug:
            logger.info("update " + table + " set authz_response_code=\"" + req_token + "\" where uuid=\"" + uuid +
                        "\"  and  device_uuid =\"" + device_uuid + "\"")
        logger.info("**** Done: In SLR models - update_authz_response_code_device_uuid ****")

    def update_entitlement_tag(self, table, uuid, ip_addr, entitlement_license_tag):
        logger.info("**** Start: In SLR models - update_entitlement_tag ****")
        self.db.query(
            "update " + table + " set license_entitlement_tag=\"" + entitlement_license_tag + "\" where uuid=\"" +
            uuid + "\" and ipaddr =\"" + ip_addr + "\"")
        if slr_debug:
            logger.info(
                "update " + table + " set license_entitlement_tag=\"" + entitlement_license_tag + "\" where uuid=\""
                + uuid + "\" and ipaddr =\"" + ip_addr + "\"")
        logger.info("**** Done: In SLR models - update_entitlement_tag ****")

    def update_license_count(self, table, uuid, ip_addr, lic_count_string):
        logger.info("**** Start: In SLR models - update_license_count ****")
        self.db.query(
            "update " + table + " set license_count=\"" + lic_count_string + "\" where uuid=\"" + uuid + "\" and "
                                                                                                         "ipaddr =\""
            + ip_addr + "\"")
        if slr_debug:
            logger.info(
                "update " + table + " set license_count=\"" + lic_count_string + "\" where uuid=\"" + uuid + "\" and "
                                                                                                             "ipaddr "
                                                                                                             "=\"" +
                ip_addr + "\"")
        logger.info("**** Done: In SLR models - update_license_count ****")

    def find_by_status(self, table, uuid, status):
        logger.info("**** Start: In SLR models - find_by_status ****")
        rows = self.db.query(
            "select * from " + table + " where status = \"" + status + "\" and uuid = \"" + uuid + "\"")
        if slr_debug:
            logger.info(rows)
        logger.info("**** Done: In SLR models - find_by_status ****")
        return rows

    def find_by_step_status(self, table, uuid, status, step):
        logger.info("**** Start: In SLR models - find_by_step_status ****")
        rows = self.db.query(
            "select * from " + table + " where " + step + "= \"" + status + "\" and uuid = \"" + uuid + "\"")
        if slr_debug:
            logger.info(rows)
        logger.info("**** Done: In SLR models - find_by_step_status ****")
        return rows

    def get_license_count(self, row):
        logger.info("**** Start: In SLR models - get_license_count ****")
        logger.info("**** Done: In SLR models - get_license_count ****")
        return row[8]

    def get_license(self, row):
        logger.info("**** Start: In SLR models - get_license ****")
        logger.info("**** Done: In SLR models - get_license ****")
        return row[7]

    def __del__(self):
        del self.db
