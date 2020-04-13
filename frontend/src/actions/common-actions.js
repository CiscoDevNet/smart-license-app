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

import { history } from '../helpers/history';

export const commonAction = {
    goToHome,
    cancelClicked,
    logout,
    reqCodeGen,
    nextStep3,
    getAuthKeys,
    nextStep4,
    applyAuthKeys
}

function goToHome() {
    console.log('Home Clicked !!!');
    history.push('/Home');
}

function cancelClicked() {
    console.log('Cancel Clicked !!!');
    history.push('/Home');
}

function logout() {
    console.log('Logout Clicked !!!');
    localStorage.removeItem('loggedInUser');
    history.push('/AppLogin');

}

// Temp SLR 

function reqCodeGen() {
    console.log('Generate Req Code Clicked !!!');
    history.push('/slrStep2ReqCodeStatus');
}

function nextStep3() {
    console.log('Next Step 3 Clicked !!!');
    history.push('/slrStep3GetAuthKeys');
}

function getAuthKeys() {
    console.log('Get Authorization Codes Clicked !!!');
    history.push('/slrStep3GetAuthKeysStatus');
}

function nextStep4() {
    console.log('Next Step 4 Clicked !!!');
    history.push('/slrStep4ApplyAuthKeys');
}

function applyAuthKeys() {
    console.log('Apply Authorization Codes Clicked !!!');
    history.push('/slrStep4ApplyAuthKeysStatus');
}