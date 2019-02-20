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

import { alertAction } from './';
import { registerConstant } from '../constants';
import { history } from '../helpers/history';

import axios from 'axios';
import { uploadConstant } from "../constants/upload-constants";

export const RegisterAction = {
  register
};

function register() {
  return dispatch => {
    dispatch(request());
    registerProcess()
      .then(
        registerRsp => {
          dispatch(success(registerRsp));
          history.push('/uploadedDevices');
        },
        error => {
          dispatch(failure(error.toString()));
          dispatch(alertAction.error(error.toString()));
        }
      );
  };

  function request() {
    return {
      type: registerConstant.REGISTER_REQUEST,
    }
  }

  function success(uploadRsp, uploadedFile) {
    return {
      type: registerConstant.FILE_UPLOAD_SUCCESS,
      uploadRsp, uploadedFile
    }
  }
  function failure(error) { return { type: uploadConstant.FILE_UPLOAD_FAILURE, error } }
}

function registerProcess() {
  console.log('CSV File Upload Service - begin');

  return axios.post(`/`)
    .then(handleFileUploadToServerResponse)
    .then(uploadResponse => {
      console.log('uploadRsp:' + JSON.stringify(uploadResponse));
      if(uploadResponse.uuid) {
        localStorage.setItem('uploadRsp', JSON.stringify(uploadResponse));
      }
      return uploadResponse;
    });
}

function handleFileUploadToServerResponse(response) {
  console.log("Handle CSV Res !!" + JSON.stringify(response));

  if (response.error) {
    console.log();
    return Promise.reject(response.error);
  }
  console.log("Handle CSV Res - No ERROR");

  if (response.data) {
    const data = response.data;
    console.log('JSON.parse(data): ' + JSON.stringify(data));
    return data;
  }
}
