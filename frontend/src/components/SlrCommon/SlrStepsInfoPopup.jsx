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

import React, { Component } from 'react';
import { Button } from "react-bootstrap";

export class SlrStepsInfoPopup extends Component {
    render() {
      return (
        <div className='slrInfoPopup'>
          <div className='slrInfoPopupInner'>
            <div className="slrInfo">
              <Button onClick={ this.props.closeSlrInfo }><span aria-hidden="true">X</span></Button>
            </div>
          <div className="container">

          <div>
            <h5>SLR Steps</h5>
          </div>

          <div className="card-deck cardContainer">
            <div className="card">
              <div className="card-header ">
                <h6>Step 1 - File Upload</h6>
              </div>
              <div className="card-body">
                <ul className="slrDescription">
                  <li>Upload a CSV file with Devices Details to start the registration.</li>
                  <li>There is a sample CSV file link given in Upload page, that can be used to prepare the CSV for registration</li>
                </ul>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h6>Step 2 - Generate Request Code</h6>
              </div>
              <div className="card-body">
                <ul className="slrDescription">
                  <li>Request Code will be generated for the uploaded devices, commands will be executed on each device.</li>
                  <li> This step must be performed in the 'Air-Gapped', 'Dark' or 'Disconnected' Netowrk, where the devices are
                    deployed. An 'Air-Gapped', 'Dark', 'Disconnected' Netowrk is a network, has no connectivity to 'Public' or 'Internet'.</li>
                  <li> If this application is not running on same network where the devices are deployed, 
                    connect to that network before executing this step.</li>
                </ul>
              </div>
            </div>


            <div className="card">
              <div className="card-header">
                <h6>Step 3 - Getting Authorization Codes from CSSM</h6>
              </div>
              <div className="card-body">
                <ul className="slrDescription">
                  <li className="card-text">Authorization Codes will be retrived from the CSSM for the uploaded devices.
                  </li>
                  <li className="card-text">Access credential for CSSM is required, will pop up to get Cisco.com 
                  login credential to connect to CSSM.
                  </li>
                  <li className="card-text">This step must be performed in the public network or on internet, 
                    where Cisco CSSM API gateway is accessible.</li>
                  <li className="card-text">If this application is not running on public or internet accessible 
                  network, connect to that network before executing this step.</li>
                </ul>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h6>Step 4 - Applying Authorization Codes on Devices</h6>
              </div>
              <div className="card-body">
                <ul className="slrDescription">
                  <li className="card-text">Authorization Codes will be applied to each device from the list of uploaded devices for registration</li>
                  <li className="card-text">This step must be performed back again in the 'Air-Gapped', 'Dark' or 'Disconnected' 
                    Netowrk, where the devices are deployed.</li>
                  <li className="card-text">If this application is not running on same network where the devices are deployed,
                    connect to that network before executing this step.</li>
                </ul>
              </div>
            </div>
          </div>
          &nbsp;<br/>&nbsp;
        </div>
        </div>
        </div>
      );
    }
  }
