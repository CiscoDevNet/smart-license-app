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
import { history } from '../helpers'

export const loginAction = {
    login
}

export var JWTToken = ""
function login(username, password) {
    return dispatch => {
        authenticateLogIn(username, password)
        .then(
            user => {
                dispatch (success(user));
                localStorage.setItem('loggedInUser', user);
                history.push('/Home')
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

function authenticateLogIn(username, password) {
    console.log("Login to app")
    const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'
                      },
            body: JSON.stringify({ username, password })
    };

    return fetch(`/auth`, requestOptions)
        .then(handleResponse)
        .then(user => {
            console.log('loggedInUser:' + JSON.stringify(user));
            if (user.token) {
                localStorage.setItem('loggedInUser', JSON.stringify(user));
            }
            return prepareLoginInfo(username, user);
        });
}

function handleResponse(response) {
    return response.text().then(text => {
        const data = text && JSON.parse(text);
        console.log('Response Type: ' + response.type + ',  Status: ' + response.ok);
        if (!response.ok) {
            console.log("Bad Response");
            if (response.status === 401) {
                logout();
            }
            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
        }
        console.log("Good Response: " + JSON.stringify(data));
        return data;
    });
}

function logout() {
    localStorage.removeItem('loggedInUser');
    history.push("/AppLogin")
}

function prepareLoginInfo(username, apiRsp) {
    const apiRspObj = apiRsp;
    JWTToken = apiRspObj['access_token'];
    const loginInfo = JSON.stringify({
        'JWTToken': apiRspObj['access_token'],
    });
    return loginInfo;
}

