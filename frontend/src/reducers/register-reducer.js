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

import { registerConstant } from '../constants';
import { slrConstant } from "../constants/slr-constants";

const initialState = {
  registerResponse: {},
  uuid: '',
  previousRegistrations: [],
  currentStep: slrConstant.SLR_STEP_1_STARTED,
  registrationType: 'sl',
};

export function register(state = initialState, action) {
  switch (action.type) {
    case registerConstant.REGISTER_SUCCESS: {
      const newState = {
        ...state,
        registerResponse: action.registerResponse,
        uuid: action.registerResponse.uuid,
      }
      return newState;
    }

    case registerConstant.SET_REGISTRATIONS_UUID: {
      const { registrationType, status, uuid } = action;
      const newState = {
        ...state,
        uuid,
        registrationType:registrationType,
        status,
      }
      return newState;
    }

    case registerConstant.PREVIOUS_REGISTRATIONS_SUCCESS: {
      console.log("register action:", {...action});
      const newState = {
        ...state,
        previousRegistrations: [...action.previousRegistrations],
      }
      return newState;
    }

    case registerConstant.SET_REGISTRATIONS_TYPE: {
      const {registrationType } = action;
      console.log('registerConstant.SET_REGISTRATIONS_TYPE: ',registrationType);
      const newState = {
        ...state,
        registrationType:registrationType,
      };
      return newState;
    }

    default:
      return state;
  }
}
