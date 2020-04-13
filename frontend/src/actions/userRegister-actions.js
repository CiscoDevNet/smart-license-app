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
import { userRegisterConstant } from '../constants';
import { history } from '../helpers'

export const userRegisterAction = {
    register
};

function register(user) {
    return dispatch => {
        registrationService(user)
            .then(
                user => {
                    dispatch(success(user));
                    history.push('/AppLogin')
                    dispatch(alertAction.success('Registration successful'));
                },
                error => {
                    dispatch(failure(error.toString()));
                    dispatch(alertAction.error(error.toString()));
                }
            );
    };

    function success(user) { return { type: userRegisterConstant.USER_REGISTER_REQUEST, user } }
    function failure(error) { return { type: userRegisterConstant.USER_REGISTER_SUCCESS, error } }
}


function registrationService(user){
    const requestOptions = {
            method: 'POST',
            headers: {  'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'

                     },
            body: JSON.stringify(user)
        };

        return fetch(`/register`, requestOptions)
        .then(handleResponse);
    }

function handleResponse(response) {
    return response.text().then(text => {
        console.log("Text: " + text);
        const data = text && JSON.parse(text);
        if (!response.ok) {
            if (response.status === 401) {
               console.log("Bad Response")
            }
            const error = (data && data.message) || response.statusText;
            return Promise.reject(error);
        }
        return data;
    });
}
