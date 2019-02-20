/**
 * Copyright (c) 2019 Cisco and/or its affiliates.
 * 
 * This software is licensed to you under the terms of the Cisco Sample
 * Code License, Version 1.1 (the "License"). You may obtain a copy of the
 * License at
 * 
 *                https://developer.cisco.com/docs/licenses
 * 
 * All use of the material herein must be in accordance with the terms of
 * the License. All rights not expressly granted by the License are
 * reserved. Unless required by applicable law or agreed to separately in
 * writing, software distributed under the License is distributed on an "AS
 * IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied.
 */

export const commonConstants = {
  SET_UUID: 'SMART_LIC_SET_UUID',
  RESET_UUID: 'SMART_LIC_RESET_UUID',

};

export const deviceStatus = {
  'csv_file_uploaded': 'CSV Upload - Completed',
  'sls':	'Started',
  'slc':	'Completed',
  's1c':	'CSV Upload - Completed',
  's2s':	'Request Code Generation on Device - Started',
  's2c':	'Request Code Generation on Device - Completed',
  's3s':	'Auth Key Request on CSSM - Started',
  's3c':	'Auth Key Request on CSSM - Completed',
  's4s':	'Applying Auth Key Request on Device - Started',
  's4c':	'Completed'
};

export const deviceStatusKey = {
  'csv_file_uploaded': 'csv_file_uploaded',
  'sls':	'sls',
  'slc':	'slc',
  's1c':	's1c',
  's2s':	's2s',
  's2c':	's2c',
  's3s':	's3s',
  's3c':	's3c',
  's4s':	's4s',
  's4c':	's4c'
};
