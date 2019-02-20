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

import {toasterType} from '../constants/toaster-constants';
import {toast} from 'react-toastify';
import React from "react";

export function toaster(httpStatusCode,message){
  let type;

  if(httpStatusCode === 200 || httpStatusCode === 201){
    type = toasterType.SUCCESS;
  }else {
    type = toasterType.ERROR;
  }

  let toasterClass;

  switch(type){
    case toasterType.ERROR: {
      toasterClass = "fa fa-exclamation-triangle fa-3x text-danger";
      break;
    }

    case toasterType.WARNING: {
      toasterClass = "fa fa-exclamation-triangle fa-3x text-warn";
      break;
    }

    case toasterType.SUCCESS: {
      toasterClass = "fa fa-check-circle fa-3x text-success";
      break;
    }

    case toasterType.INFO: {
      toasterClass = "fa fa-exclamation-triangle fa-3x text-info";
      break;
    }

    default:
      toasterClass = "fa fa-exclamation-triangle fa-3x";
      break;
  }
  return (
    toast(() => {
        return (
          <div className="toasterDiv">
            <div className="icon">
              <i className={toasterClass} />
            </div>
            <div className="errorMessage">{message}</div>
          </div>
        )
      },{autoClose: false}
    )
  );
}
