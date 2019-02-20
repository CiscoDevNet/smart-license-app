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

import { commonConstants } from '../constants/common-constants';
const initialState = {
  uuid: '',
};

export function common(state = initialState, action) {
  switch (action.type) {
    case commonConstants.SET_UUID: {
      const newState = {
        uuid: action.uuid,
      };
      return newState;
    }

    case commonConstants.RESET_UUID: {
      const newState = {
        uuid: '',
      };
      return newState;
    }

    default:
      return state;
  }
}
