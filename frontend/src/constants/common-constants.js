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
  's2sx':	'Request Codes - Export Started',
  's2si':	'Request Codes - Import Started',
  's2cx':	'Request Codes - Export Completed',
  's2ci':	'Request Codes - Import Completed',
  's2fx':	'Request Codes - Export Failed',
  's2fi':	'Request Codes - Import Failed',
  's3s':	'Get Authorization Codes from CSSM - Started',
  's3c':	'Get Authorization Codes from CSSM - Completed',
  's3sx':	'Authorization Codes - Export Started',
  's3si':	'Authorization Codes - Import Started',
  's3cx':	'Authorization Codes - Export Completed',
  's3ci':	'Authorization Codes - Import Completed',
  's3fx':	'Authorization Codes - Export Failed',
  's3fi':	'Authorization Codes - Import Failed',
  's4s':	'Applying Authorization Code on Device - Started',
  's4c':	'Completed'
};

export const deviceStatusKey = {
  'csv_file_uploaded': 'csv_file_uploaded',
  'sls':	'sls',
  'slc':	'slc',
  's1c':	's1c',
  's2s':	's2s',
  's2c':	's2c',
  's2sx':  's2sx',
  's2si':  's2si',
  's2cx':  's2cx',
  's2ci':  's2ci',
  's2fx':  's2fx',
  's2fi':  's2fi',
  's3s':	's3s',
  's3c':	's3c',
  's3sx':	's3sx',
  's3si':	's3si',
  's3cx':	's3cx',
  's3ci':	's3ci',
  's3fx':	's3fx',
  's3fi':	's3fi',
  's4s':	's4s',
  's4c':	's4c'
};
