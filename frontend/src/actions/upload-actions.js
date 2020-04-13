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
import { commonConstants, uploadConstant } from '../constants';
import { history } from '../helpers/history';

export const uploadAction = {
    upload
}

function upload(file, type) {
    console.log('File type being uploaded :', type);
    return dispatch => {
        dispatch(request({ file }));
        fileUploadToServer(file,type)
            .then(
                uploadRsp => {
                    console.log({ uploadRsp });
                    dispatch(success(uploadRsp, file));
                    if ('sl' === type) {
                        history.push('/uploadedDevices');
                    } else if ('slr' === type) {
                        history.push('/slrStep2ReqCode');
                    }
                  dispatch({
                    type: commonConstants.SET_UUID,
                    uuid: uploadRsp.uuid,
                  });
                },
                error => {
                    dispatch(failure(error.toString()));
                    dispatch(alertAction.error(error.toString()));
                }
            );
    };

    function request(uploadedFile) { return { type: uploadConstant.FILE_UPLOAD_REQUEST, uploadedFile } }
    function success(uploadRsp, uploadedFile) {
        return {
            type: uploadConstant.FILE_UPLOAD_SUCCESS,
          uploadRsp, uploadedFile
        }
    }
    function failure(error) { return { type: uploadConstant.FILE_UPLOAD_FAILURE, error } }
}

function fileUploadToServer(file,type) {
    console.log('CSV File Upload Service - File type:',type);
    const data = new FormData()
    data.append('file', file, file.name);
    data.append('registration_type', type || 'sl');
    data.append('oauth_token', 'x')
     const requestOptions = {
            method: 'POST',
            headers:{
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
            },
            body: data
    };

    return fetch(`/upload`, requestOptions)
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
    return response.text().then(text => {
        const data = text && JSON.parse(text);
        console.log('Response Type: ' + response.type + ',  Status: ' + response.ok);
        if (!response.ok) {
            if (response.status === 401) {
                history.push('/AppLogin')
                localStorage.removeItem('loggedInUser');
            }
            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
        }
        console.log("Handle CSV Res - No ERROR");
        console.log('JSON.parse(data): ' + JSON.stringify(data))
        return data;
     });
}
