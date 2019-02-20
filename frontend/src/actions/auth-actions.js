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

import { authConstant } from '../constants/auth-constants';
import { alertAction } from './';

export const authAction = {
    login
}

function login(username, password, actionAfterLogin) {
    return dispatch => {
        authenticateUsingService(username, password)
        .then(
            user => {
                dispatch (success(user));
                localStorage.setItem('user', user);
                //history.push('/');
                dispatch(actionAfterLogin)
            },
            error => {
                dispatch (failure(error));
                dispatch (alertAction.error(error.toString()));
            }
        );
    };
    function success(user) { return { type: authConstant.LOGIN_SUCCESS, user } }
    function failure(error) { return { type: authConstant.LOGIN_FAILURE, error } }
}

function authenticateUsingService(username, password) {
    console.log("Login Service !!")
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                    'rejectUnauthorized': 'false',
                    'requestCert': 'false',
                    'agent': 'false',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'
                },
        //headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
        body: JSON.stringify({ username, password })
    };

    return fetch(`/authen`, requestOptions)
        .then(handleResponse)
        .then(user => {
            console.log('User:' + JSON.stringify(user));
            if (user.token) {
                localStorage.setItem('user', JSON.stringify(user));
            }

            return prepareUserInfo(username, user);
        });
}

function handleResponse(response) {
    console.log("Handle Res !!" + JSON.stringify(response))
    return response.text().then(text => {
        console.log("Text: " + text);
        const data = text && JSON.parse(text);
        console.log('Response Type: ' + response.type + ',  Status: ' + response.ok);
        if (!response.ok) {
            console.log("Bad Response");
            if (response.status === 401) {
                // auto logout if 401 response returned from api
                clearLocalStorageAuthData();
                //location.reload(true);
            }

            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
        }
        console.log("Good Response: " + JSON.stringify(data));

        return data;
    });
}

function clearLocalStorageAuthData() {
    localStorage.removeItem('user');
}

function prepareUserInfo(username, apiRsp) {
    const apiRspObj = apiRsp;
    let loggedInTimeInMS = Date.now();
    const userInfo = JSON.stringify({
        'userName': username,
        'loggedInTimeInMS': loggedInTimeInMS,
        'authToken': apiRspObj['access_token'],
        'refreshToken': apiRspObj['refresh_token'],
        'tokenType': apiRspObj['token_type'],
        'expiresInSecs': apiRspObj['expires_in']
    });
    return userInfo;
}


