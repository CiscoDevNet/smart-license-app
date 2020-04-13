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

let user = JSON.parse(localStorage.getItem('loggedInUser'));
const initialState = user ? { loggedIn: true, user } : {};

export function appLogin (state = initialState, action) {
  switch (action.type) {
    case authConstant.LOGIN_REQUEST:
      return {
        loggedIn: true,
        user: action.user
      };
    case authConstant.LOGIN_SUCCESS:
      return {
        loggedIn: true,
        user: action.user
      };
    case authConstant.LOGIN_FAILURE:
      return {};
    case authConstant.LOGOUT:
      return {};
    default:
      return state
  }
}