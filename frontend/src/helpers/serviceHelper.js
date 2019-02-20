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

import { deviceStatusKey } from "../constants/common-constants";
import { slrConstant } from "../constants/slr-constants";


/**
 * Get oauth token.
 * @param input: user object from store
 * @return oauth token
 */
export function getAuthToken(user) {
  let token, tokenType;

  if (typeof user === typeof {}) {
    token = user.authToken;
    tokenType = user.tokenType;
  } else if (typeof user === typeof "string") {
    const userJson = JSON.parse(user);
    token = userJson.authToken;
    tokenType = userJson.tokenType
  }

  console.log({ tokenType });
  if (tokenType === undefined) {
    tokenType = 'Bearer';
  }
  // return `${tokenType} ${token}`;
  return `${ token }`;
}


/**
 * Get Registration Status.
 * @param input: uuid for which status is required
 * @return oauth token
 */
export function getRegistrationStatus(uuid) {
  const url = `/registration/status/${ uuid }`;
  console.log({ url });
  return fetch(url);
}

export function isEnableButton(currentStatus, currentStepNumber) {
  switch (currentStepNumber) {
    case 2:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.csv_file_uploaded.toLowerCase() ||
        deviceStatusKey.s1c.toLowerCase() ||
        deviceStatusKey.s2s.toLowerCase() ||
        deviceStatusKey.s2c.toLowerCase() ||
        deviceStatusKey.s3s.toLowerCase() ||
        deviceStatusKey.s3c.toLowerCase() ||
        deviceStatusKey.s4s.toLowerCase() ||
        deviceStatusKey.s4c.toLowerCase()
      );

    case 3:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.s2c.toLowerCase() ||
        deviceStatusKey.s3s.toLowerCase() ||
        deviceStatusKey.s3c.toLowerCase() ||
        deviceStatusKey.s4s.toLowerCase() ||
        deviceStatusKey.s4c.toLowerCase()
      );

    case 4:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.s3c.toLowerCase() ||
        deviceStatusKey.s4s.toLowerCase() ||
        deviceStatusKey.s4c.toLowerCase()
      );

    case 5:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.s4c.toLowerCase()
      );

    case 22:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.s2s.toLowerCase() ||
        deviceStatusKey.s2c.toLowerCase() ||
        deviceStatusKey.s3s.toLowerCase() ||
        deviceStatusKey.s3c.toLowerCase() ||
        deviceStatusKey.s4s.toLowerCase() ||
        deviceStatusKey.s4c.toLowerCase()
      );

    case 32:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.s3s.toLowerCase() ||
        deviceStatusKey.s3c.toLowerCase() ||
        deviceStatusKey.s4s.toLowerCase() ||
        deviceStatusKey.s4c.toLowerCase()
      );

    case 42:
      return currentStatus.toLowerCase() === (
        deviceStatusKey.s4s.toLowerCase() ||
        deviceStatusKey.s4c.toLowerCase()
      );

    default:
      return;

  }
}

export function needsLoginCheck(userInfo) {
  let udf; // Undefined
  let needsLogin = false;
  if ( typeof userInfo !== typeof udf && userInfo !== null) {
    let oAuthToken, loggedInTimeInMS, expiresInSecs
    if (typeof userInfo === typeof {}) {
      oAuthToken = userInfo.authToken;
      loggedInTimeInMS = userInfo.loggedInTimeInMS;
      expiresInSecs = userInfo.expiresInSecs;
    } else if (typeof user === typeof "string") {
      const userInfoJson = JSON.parse(userInfo);
      oAuthToken = userInfoJson.authToken;
      loggedInTimeInMS = userInfoJson.loggedInTimeInMS;
      expiresInSecs = userInfoJson.expiresInSecs;
    }

    let now = Date.now();
    let elapsed = now - loggedInTimeInMS;

    let offset = 14 * 60 * 1000; // 14 mins, which means, token is valid for 45mins(59-14), when it expires in 59mins
    let delta = (expiresInSecs * 1000) - offset - elapsed;

    console.log("O Auth: " + oAuthToken + ", Expires In Secs: " + expiresInSecs);
    console.log("Logged In: " + loggedInTimeInMS + ", now: " + now + ", elapsed: " + elapsed + ", delta: " + delta);

    if (!Number.isNaN(delta) && delta > 0 ) { // Token is good for registration
      needsLogin = false;
    } else { // Time to refresh or get a new token
      needsLogin = true;
    }

  } else {
    needsLogin = true;
  }
  return needsLogin;
}

export function slrCurrentStep() {
  let toSlrStep;
  const currentStep = this.state.currentStep !== undefined ? this.state.currentStep.toLowerCase() : undefined;
  if ( currentStep === slrConstant.SLR_STEP_1_COMPLETED.toLowerCase() ||
       currentStep === 'sls' || currentStep === 'csv_file_uploaded'.toLowerCase() )
  {
    toSlrStep = 'slrStep2ReqCode';
  } else if (currentStep === slrConstant.SLR_STEP_2_COMPLETED.toLowerCase()) {
    toSlrStep = 'slrStep3GetAuthKeys';
  } else if (currentStep === slrConstant.SLR_STEP_3_COMPLETED.toLowerCase()) {
    toSlrStep = 'slrStep4ApplyAuthKeys';
  }
  return toSlrStep;
}