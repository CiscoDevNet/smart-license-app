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

import fetchIntercept from 'fetch-intercept';
import { JWTToken } from './'
import { commonAction } from './'

export const unregister = fetchIntercept.register({
    request: function (url, config) {
        console.log("Inside interceptor request");
        console.log("loginInfo in interceptor", JWTToken )
        if ( JWTToken !==  "" ) {
            config.headers.Authorization = `JWT ${JWTToken}`
        }
        return [url, config];
    },

    requestError: function (error) {
        return Promise.reject(error);
    },

    response: function (response) {
       return response;
    },

    responseError: function (error) {
        commonAction.logout()
        return Promise.reject(error);
    }
});
