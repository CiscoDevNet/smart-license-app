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

import React from 'react';
import { connect } from 'react-redux';
import { Panel } from 'react-bootstrap';
import UltimatePaginationBootstrap from 'react-ultimate-pagination-bootstrap-4';
import loadingImage from '../../resources/images/Loading.gif';
import { commonAction } from '../../actions';
import { registerConstant } from "../../constants";
import Stepper from 'react-stepper-horizontal';
import { toaster } from "../../helpers/toasterHelper";
import { getRegistrationStatus, isEnableButton } from "../../helpers/serviceHelper";
import ReactTooltip from 'react-tooltip';
import { SlrStepsInfoPopup } from '../SlrCommon/SlrStepsInfoPopup';
import Modal from 'react-bootstrap4-modal';

const passwordMask = '********';

class SlrStep2ReqCode extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      devices: null,
      page: localStorage.getItem('page') ? localStorage.getItem('page') : 1,
      totalPages: 1,
      alertModal: false,
      isEnableButton: false,
      showSlrInfoPopupS2: false
    };
    this.modalRef = null;
    this.modalMessage = '';
    this.handleBackToSlrStepsClick = this.handleBackToSlrStepsClick.bind(this);
    this.handleRegisterDevices = this.handleRegisterDevices.bind(this);
    this.onPageChange = this.onPageChange.bind(this);
    this.handleGenerateReqCodes = this.handleGenerateReqCodes.bind(this);
    this.hideLoadingModal = this.hideLoadingModal.bind(this);
    this.showLoadingModal = this.showLoadingModal.bind(this);
    this.toggleButton = this.toggleButton.bind(this);
    this.fetchDevicePage = this.fetchDevicePage.bind(this);
    this.infodivclickS2 = this.infodivclickS2.bind(this);
  }

    componentWillMount() {
    console.log('componentWillMountProps:',this.props);
    this.fetchDevicePage(1);
    this.toggleButton();
  }

  async toggleButton(){
    const uuid = this.props.uuid || this.props.upload.uploadRsp.uuid;

    const respObj = await getRegistrationStatus(uuid);
    const resp = await respObj.json();
    const actualResp = {
      ...resp,
      status: respObj.status,
    };

    this.hideLoadingModal();
    if (actualResp.status === 200 || actualResp.status === 201) {
      /*TODO: write a method that will give true or false based on status given by backend.*/
      const showButton = isEnableButton(resp.status,2);
      this.setState({
        isEnableButton: showButton,
      });
      console.log({ actualResp });
      console.log('showButton:',showButton);

    } else {
      console.log('Need to handle error!');
      toaster(actualResp.status, actualResp.message);
    }
  }

  handleBackToSlrStepsClick(event) {
    event.preventDefault();
    commonAction.backToSlrStepsClicked();
  }



  handleRegisterDevices() {
    this.modalMessage = 'Initiating Registration....';
    console.log("Props:", { ...this.props });

    const user = (this.props.auth.user);
    let token = user.authToken;

    if (typeof user === typeof {}) {
      token = user.authToken;
    } else if (typeof user === typeof "string") {
      const userJson = JSON.parse(user);
      token = userJson.authToken;
    }
    console.log({ token });

    const { uuid } = this.props.upload.uploadRsp;
    const { dispatch } = this.props;
    let uri = `/sl/tokens/${uuid}`;
    fetch(uri, {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ oauth_token: token }),
    }).then(handleResponse)
      .then(registerStatus => {
        console.log('Modal Ref:', this.modalRef);
        console.log('registerStatus: ', { registerStatus });
        dispatch({
          type: registerConstant.REGISTER_SUCCESS,
          registerResponse: registerStatus,
        });
        this.props.history.push('/registrationStatus');
      })
      .catch(errorResponse => {
        this.modalMessage = `Registration Initiation Failed: ${errorResponse}`;
        console.log(errorResponse)
      })
  }

  onPageChange(page) {
    console.log({ page });
    this.setState({ page });
    this.fetchDevicePage(page);
  }

  fetchDevicePage(pageNumber) {
    const uuid = this.props.uuid || this.props.upload.uploadRsp.uuid;
    console.log('props:',this.props );
    let uri = `/devicesuploaded/${uuid}/${pageNumber}`;
    console.log('UUID: ' + uuid + ',  Page: ' + pageNumber + ', URI: ' + uri);
    fetch(uri)
      .then(handleResponse)
      .then(devicesUploaded => {
        console.log("devices:", devicesUploaded.devices);
        this.setState({
          devices: devicesUploaded.devices,
        });
        console.log('Devices Uploaded: ' + JSON.stringify(devicesUploaded));
      })
  }

  showLoadingModal() {
    this.setState({ alertModal: true });
  }

  hideLoadingModal() {
    this.setState({ alertModal: false });
  }

  generateRequestCode(){
    const { uuid } = this.props;
    const url = `/slr/device/reqcode/${uuid}`;
  console.log({ url });
    return fetch(url);
  }

  async handleGenerateReqCodes(event) {
    console.log('Generate Req Codes clicked');
    this.showLoadingModal();
    const respObj = await this.generateRequestCode();
    const resp = await respObj.json();
    const actualResp = {
      status: respObj.status,
      ...resp,
    };
    console.log({ resp });
    console.log({ actualResp });

    this.hideLoadingModal();
    if( actualResp.status === 201 || actualResp.status === 200){
      this.props.history.push('/slrStep2ReqCodeStatus');
    }else {
      toaster(resp.status, actualResp.message);
    }
  }

  infodivclickS2() {
    this.setState({showSlrInfoPopupS2: true});
  }

  closeSlrInfoPopupS2() {
    this.setState({ showSlrInfoPopupS2: false })
  }

  render() {
    let devices = this.state.devices;

    let devicesRows = <tr>
      <th colSpan="6" className="text-nowrap font-weight-normal text-center"><img
        src={ loadingImage } alt="Loading ..."/></th>
    </tr>;
    if (devices) {
      if (devices.length === 0) {
        devicesRows = <tr>
          <th colSpan="6" className="text-nowrap font-weight-normal text-center">No Device</th>
        </tr>;
      } else {
        devicesRows = devices.map(
          (device, index) => {
            return <tr key={ `device['ipaddr']: ${index}` }>
              <th className="text-nowrap font-weight-normal">{ device['ipaddr'] }</th>
              <th className="text-nowrap font-weight-normal">{ device['username'] }</th>
              <th className="text-nowrap font-weight-normal">{ passwordMask }</th>
              <th className="text-nowrap font-weight-normal">{ device['sa_name'] }</th>
              <th className="text-nowrap font-weight-normal">{ device['domain'] }</th>
              <th className="text-nowrap font-weight-normal">{ device['va_name'] }</th>
            </tr>;
          }
        );
      }
    }

    // let pagination = getPagination(3);

    return (
      <div>
        {/*Modal*/}
        <div>
          <Modal visible={ this.state.alertModal } className="transparentModal spinnerModal">
            <div className="modal-body">
              <div className="loader"></div>
            </div>
          </Modal>
        </div>

        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item " aria-current="page">Home</li>
              <li className="breadcrumb-item active" aria-current="page">SLR Step 2: Generating
                Request Code on Devices
              </li>
            </ol>
          </nav>
        </div>


        <div className="container">
        <div className="slrInfo" onClick={this.infodivclickS2}>
            <a id="slrinfoPopuplink" href="#click">
            <i data-tip data-for="slrInfo" className="fa fa-info-circle text-primary"></i>
            <ReactTooltip className='opaque' id="slrInfo" type='light'>Click here for SLR Information</ReactTooltip>
            </a>
          </div>
          <div className="stepper">
            <Stepper steps={ [
              { title: 'Device Details Upload' },
              { title: '' },
              { title: 'Getting Auth Code from CSSM' },
              { title: 'Applying Auth Code on Devices' }
            ] }
                     activeStep={ 1 }
                     activeColor="#007bff"
                     completeColor="#28a745"
            />
          </div>
          <div className="gridDisplay">
            <div className="gridDisplay">
              <section>
                { /*<h4>SLR Step 2: Generating Request Code on Devices</h4>*/ }
                { /*<hr/>*/ }
                <div className="card">
                  <div className="card-header">
                    <h4>SLR Step 2: Generating Request Code on Devices</h4>
                  </div>
                  <div className="card-body">
                    <p className="card-text"></p>
                    <div className="text-center">
                      <table className="table table-bordered table-sm table-hover">
                        <thead>
                        <tr>
                          <th className="text-nowrap text-center">Device IP</th>
                          <th className="text-nowrap text-center">User Name</th>
                          <th className="text-nowrap text-center">Password</th>
                          <th className="text-nowrap text-center">Smart Account</th>
                          <th className="text-nowrap text-center">Smart Account Domain</th>
                          <th className="text-nowrap text-center">Virtual Account</th>
                        </tr>
                        </thead>
                        <tbody>
                        { devicesRows }
                        </tbody>
                      </table>
                    </div>
                    <div className="text-left">
                      <Panel>
                        <Panel.Body>
                          <p>
                          <div className="stepMessageWarningContainer">
                            <div className="stepMessageWarning">
                              <div className="slrStepIcon">
                                <i className="fa fa-exclamation-triangle text-warning"></i>
                              </div>
                              <div className="slrStepWarningDescription">
                                This step should be executed on the network where the devices are connected and reachable
                              </div>
                            </div>
                            <div className="stepMessageWarning">
                              <div className="slrStepIcon">
                                <i className="fa fa-exclamation-triangle text-warning"></i>
                              </div>
                              <div className="slrStepWarningDescription">
                                Make sure you are connected to the devices network(Disconnected/Dark/Air-Gapped Network)
                              </div>
                            </div>
                            <div className="stepMessageWarning">
                              <div className="slrStepIcon">
                                <i className="fa fa-exclamation-triangle text-warning"></i>
                              </div>
                              <div className="slrStepWarningDescription">
                                Click on <b>'Generate'</b> to initiate this step
                              </div>
                            </div>
                          </div>
                          </p>
                        </Panel.Body>
                      </Panel>
                    </div>
                    <div className="actionButtonGroup3">
                      <button className="btn btn-primary"
                              onClick={ () => this.props.history.push('/') }
                      >Home
                      </button>
                      <UltimatePaginationBootstrap
                        className="customPagination"
                        totalPages={ this.state.totalPages }
                        currentPage={ this.state.page }
                        onChange={ this.onPageChange }
                      />
                      <button className="btn btn-primary"
                              onClick={ this.handleGenerateReqCodes }>Generate
                      </button>
                    </div>
                  </div>
                </div>

              </section>
            </div>
          </div>
        </div>
        {this.state.showSlrInfoPopupS2 ? <SlrStepsInfoPopup closeSlrInfo={this.closeSlrInfoPopupS2.bind(this)}/> : null}

      </div>
    )
      ;
  }
}

const mapStateToProps = state => ({
  auth: state.auth,
  alert: state.alert,
  upload: state.upload,
  uuid: state.common.uuid,
});

function handleResponse(response) {
  console.log("Handle Res !!" + JSON.stringify(response))
  return response.text().then(text => {
    console.log("Text: " + text);
    const data = text && JSON.parse(text);
    console.log('Response Type: ' + response.type + ',  Status: ' + response.ok);
    if (!response.ok) {
      console.log("Bad Response");

      const error = (data && data.message) || response.statusText;
      return Promise.reject(error);
    }
    console.log("Good Response: " + JSON.stringify(data));

    return data;
  });
}


const connectedSlrStep2ReqCode = connect(mapStateToProps)(SlrStep2ReqCode);
export { connectedSlrStep2ReqCode as SlrStep2ReqCode };
