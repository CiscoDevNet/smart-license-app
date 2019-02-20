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
import { connect } from 'react-redux';
import { registerConstant } from '../../constants/register-constant';
import { commonConstants, deviceStatus } from "../../constants/common-constants";
import '../../resources/css/Home.css';
import { slrConstant } from '../../constants/slr-constants';
import '../../resources/css/slrSteps.css';

class Home extends Component {
  constructor(props) {
    super(props);
    this.state = { type: null };
    this.handleStart = this.handleStart.bind(this);
  }

  getPreviousRegistrations(url) {
    return fetch(url);
  }

  async componentWillMount() {
    const { dispatch } = this.props;
    try {
      const prevListingsResp = await this.getPreviousRegistrations('/registrations');
      const previousListing = await prevListingsResp.json();
      console.log({ previousListing });
      if (previousListing && previousListing.devices && previousListing.devices.length) {
        dispatch({
          type: registerConstant.PREVIOUS_REGISTRATIONS_SUCCESS,
          previousRegistrations: [...previousListing.devices],
        })
      }
    } catch (e) {

    }
  }

  onClickPreviousRegistrationsHandler(uuid, registrationType, status) {
    console.log({ uuid });
    console.log({ registrationType });
    console.log({ status });


    const { dispatch } = this.props;
    dispatch({
      type: registerConstant.SET_REGISTRATIONS_UUID,
      uuid,
      registrationType,
      status,
    });

    const currentStep = status !== undefined ? status.toLowerCase() : undefined;

    if (registrationType.toLowerCase() === 'sl'){
      this.props.history.push('/registrationStatus');
    } else if(currentStep === 's4s' || currentStep === 's4c') {
      this.props.history.push('/slrStep4ApplyAuthKeysStatus');
    } else if (currentStep === slrConstant.SLR_STEP_3_COMPLETED.toLowerCase()) {
      this.props.history.push('/slrStep4ApplyAuthKeys');
    } else if (currentStep === slrConstant.SLR_STEP_3_STARTED.toLowerCase()) {
      this.props.history.push('/slrStep3GetAuthKeysStatus');
    } else if (currentStep === slrConstant.SLR_STEP_2_COMPLETED.toLowerCase()) {
      this.props.history.push('/slrStep3GetAuthKeys');
    } else if (currentStep === slrConstant.SLR_STEP_2_STARTED.toLowerCase()) {
      this.props.history.push('/slrStep2ReqCodeStatus');
    } else if ( currentStep === slrConstant.SLR_STEP_1_COMPLETED.toLowerCase() ||
                currentStep === 'sls' || currentStep === 'csv_file_uploaded'.toLowerCase() ) {
      this.props.history.push('/slrStep2ReqCode');
    }
  }

  handleStart(type){
    console.log('type:',type);
    const { dispatch, history } = this.props;
    dispatch({
      type: registerConstant.SET_REGISTRATIONS_TYPE,
      registrationType: type,
    });

    this.props.dispatch({
      type: commonConstants.RESET_UUID,
    });

    if ( type.toLowerCase() === 'sl'.toLowerCase() ){
      history.push('/upload');
    } else if ( type.toLowerCase() === 'slr'.toLowerCase() ){
      history.push('/slrStep1Upload');
    }
  }

  getRegistrationStatus(status) {
    const deviceStatusPrintable = status.toLowerCase();
    if (Object.keys(deviceStatus).indexOf(deviceStatusPrintable) !== -1) {
      return deviceStatus[deviceStatusPrintable];
    }
    return status;
  }


  render() {
    console.log('Render called from:Home');
    const previousRegistrationsData = [...this.props.previousRegistrations];
    console.log("this.props.previousRegistrations:", this.props.previousRegistrations);
    const sortedArray = previousRegistrationsData.sort(function(a, b) {
      const c = new Date(a.timestamp);
      const d = new Date(b.timestamp);
      console.log({ c })
      console.log({ d })
      return d.getTime() - c.getTime();
    });

    console.log("Sorted Array:", sortedArray);
    let previousRegistrations = <tr><td colSpan="4" className="text-nowrap font-weight-normal text-center">No Registrations</td></tr>;

    if (typeof sortedArray !== "undefined" && Array.isArray(sortedArray) && sortedArray.length > 0) {
      previousRegistrations = sortedArray.map((eachDevice, index) => {      const id = eachDevice.uuid;
      return (
        <tr key={ `${eachDevice.uuid}:${index}` }>

          <td>
            <a
              href="#reg"
              key={ `${eachDevice.uuid}` }
              onClick={ () => {
                const { registration_type, status } = eachDevice;
                this.props.dispatch({
                  type: commonConstants.SET_UUID,
                  uuid: eachDevice.uuid,
                });
                /*Set the current step to toggle buttons in slr*/
                this.onClickPreviousRegistrationsHandler(id,registration_type, status)
              }
              }
            >{ eachDevice.filename }</a>

          </td>
          <td>{ eachDevice.registration_type.toUpperCase() }</td>
          <td>{ eachDevice.timestamp }</td>
          <td>{ this.getRegistrationStatus(eachDevice.status) }</td>
        </tr>
      )
    });
  }
    return (
      <div>
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item active" aria-current="page">Home</li>
            </ol>
          </nav>
        </div>


        <div className="container">
          <div className="registration">
            <div className="newRegistration">
              <section>
                <h4>New Registration</h4>
                <hr/>
                <div className="newRegistrationBody">
                  <div className="card-deck">
                    <div className="card">
                      <div className="card-header"><h6>SL - Connected Network</h6></div>
                      <div className="card-body">
                        <p className="card-text">If your network has connectivity to Cisco Smart
                          Software Management API Server, use 'SL' option.</p>
                        <div>{ '\u00a0' }</div>
                        <div className="text-center">
                          {/*<Link to="/upload">*/}
                            <button type="button" className="btn btn-primary" onClick={() => this.handleStart('sl')}>Start
                            </button>
                          {/*</Link>*/}

                        </div>
                      </div>
                    </div>
                    { /*End of SL Card*/ }

                    <div className="card">
                      <div className="card-header"><h6>SLR - Disconnected/Dark/Air-Gapped
                        Network</h6>
                      </div>
                      <div className="card-body">
                        <p className="card-text">If your network is a Disconnected/Dark/Air-Gapped
                          Network that has no connectivity to Cisco Smart Software Management API
                          Server, use 'SLR' option</p>
                        <div className="text-center">
                            <button type="button" className="btn btn-primary" onClick={() => this.handleStart('slr')}>Start
                            </button>
                        </div>
                      </div>
                    </div>
                    { /*End of SLR Card*/ }
                  </div>
                </div>
              </section>
            </div>
            { /*End of New Registration section*/ }

            <div className="previousRegistration">
              <section>
                <h4>Previous Registration</h4>
                <hr/>
                <div className="previousRegistrationBody">
                  <div className="card">
                    { /*<div className="card-header"><h6>Previous Registrations</h6></div>*/ }
                    <div className="card-body">
                      <p className="card-text">Click on one of the following previously executed
                        Registrations to see the status</p>
                      <div className="text-center">
                        <table className="table table-bordered table-sm table-hover">
                          <thead>
                          <tr>
                            <th className="text-nowrap text-center">Name</th>
                            <th className="text-nowrap text-center">Type</th>
                            <th className="text-nowrap text-center">Completed Time</th>
                            <th className="text-nowrap text-center">Status</th>
                          </tr>
                          </thead>
                          <tbody>
                          { previousRegistrations }
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
            { /*End of previousRegistration section*/ }
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = state => ({
  previousRegistrations: state.register.previousRegistrations,
  auth: state.auth,
  uuid: state.common.uuid,
});

const connectedHome = connect(mapStateToProps)(Home);
export { connectedHome as Home };

