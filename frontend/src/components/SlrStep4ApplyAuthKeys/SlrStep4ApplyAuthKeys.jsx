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
import UltimatePaginationBootstrap from 'react-ultimate-pagination-bootstrap-4';
import '../../resources/css/loading.css';
import { Panel } from "react-bootstrap";
import ReactTooltip from 'react-tooltip';
import loadingImage from '../../resources/images/Loading.gif';
import { commonAction } from '../../actions';
import '../../resources/css/common.css';
import Stepper from 'react-stepper-horizontal';
import { toaster } from "../../helpers/toasterHelper";
import { getAuthToken, getRegistrationStatus, isEnableButton } from "../../helpers";
import { SlrStepsInfoPopup } from '../SlrCommon/SlrStepsInfoPopup';
import Modal from 'react-bootstrap4-modal';

class SlrStep4ApplyAuthKeys extends Component {

  constructor(props) {
    super(props);
    this.state = {
      registeredDevices: [],
      page: 1,
      totalPages: 1,
      alertModal: false,
      isEnableButton: false,
      showSlrInfoPopupS4: false
    };
    this.onPageChange = this.onPageChange.bind(this);
    this.hideLoadingModal = this.hideLoadingModal.bind(this);
    this.showLoadingModal = this.showLoadingModal.bind(this);
    this.handleBackToSlrStepsClick = this.handleBackToSlrStepsClick.bind(this);
    this.handleApplyAuthKeysClick = this.handleApplyAuthKeysClick.bind(this);
    this.refreshRegisterStatus = this.refreshRegisterStatus.bind(this);
    this.toggleButton = this.toggleButton.bind(this);
    this.infodivclickS4 = this.infodivclickS4.bind(this);
  }

  handleBackToSlrStepsClick(event) {
    event.preventDefault();
    commonAction.backToSlrStepsClicked();
  }

  applyAuthKey() {
    const { uuid, auth } = this.props;
    const user = auth.user;
    const token = getAuthToken(user);
    const url = `/slr/device/authkey/${ uuid }`;

    console.log({ url });
    return fetch(url, {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ oauth_token: token }),
    });
  }

  async handleApplyAuthKeysClick(event) {
    event.preventDefault();
        this.showLoadingModal();
        const respObj = await this.applyAuthKey();
        console.log({ respObj });
        const resp = await respObj.json();
        console.log({ resp });

        const actualResp = {
          status: respObj.status,
          ...resp
        };

        console.log({ actualResp });

        this.hideLoadingModal();
        if (actualResp.status === 201 || actualResp.status === 200) {
          this.props.history.push('/slrStep4ApplyAuthKeysStatus');
        } else {
          console.log({ ...actualResp.status });
          toaster(actualResp.status, actualResp.message);
        }
        console.log({ actualResp });
  }

  async refreshRegisterStatus(page) {
    const { uuid } = this.props;
    const pageNumber = typeof page === typeof 5 ? page : this.state.page;
    this.showLoadingModal();
    console.log("Step 4: UUID::" + uuid);

    const respObj = await this.fetchRegisterStatus(`/slr/register/status/${uuid}/${pageNumber}`);
    const resp = await respObj.json();
    const actualResp = {
      status: respObj.status,
      ...resp,
    };

    console.log({ actualResp });
    this.hideLoadingModal();

    if (actualResp.status === 200 || actualResp.status === 201) {
      this.setState({
        registeredDevices: [...actualResp.devices],
        totalPages: actualResp.totalpages || 1,
      });

    } else {
      console.log('Need to handle error!');
      toaster(actualResp.status, actualResp.message);
    }
    await this.toggleButton();
  }

  async componentWillMount() {
    await this.refreshRegisterStatus(1);
  }


  getAuthToken() {
    const user = (this.props.auth.user);
    let token;

    if (typeof user === typeof {}) {
      token = user.authToken;
    } else if (typeof user === typeof "string") {
      const userJson = JSON.parse(user);
      token = userJson.authToken;
    }
    return token;
  }

  fetchRegisterStatus(url) {
    return fetch(url);
  }

  showLoadingModal() {
    this.setState({ alertModal: true });
  }

  hideLoadingModal() {
    this.setState({ alertModal: false });
  }

  async toggleButton() {
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
      const showButton = isEnableButton(resp.status, 4);
      this.setState({
        isEnableButton: showButton,
      });
      console.log({ actualResp });
      console.log('showButton:', showButton);

    } else {
      console.log('Need to handle error!');
      toaster(actualResp.status, actualResp.message);
    }
  }

  async onPageChange(page) {
    console.log({ page });
    this.setState({ page });
    await this.refreshRegisterStatus(page);
  }

  infodivclickS4() {
    this.setState({showSlrInfoPopupS4: true});
  }

  closeSlrInfoPopupS4() {
    this.setState({ showSlrInfoPopupS4: false })
  }

  render() {
    const deviceList = this.state.registeredDevices !== null ? this.state.registeredDevices.map((eachDevice, index) => {
        return (
          <tr key={ `eachDevice.ipaddr:${index}` }>
            <td>{ eachDevice.ipaddr }
            &nbsp;
            <i data-tip data-for={ eachDevice.ipaddr } className="fa fa-info-circle text-primary"></i>
            <ReactTooltip id={ eachDevice.ipaddr } type='light' className='opaque'>
              <table className="table table-bordered table-condensed table-striped toolTipContent">
              <tbody>
                <tr>
                  <td><b>Username</b></td>
                  <td>{ eachDevice.username }</td>
                </tr>
                <tr>
                  <td><b>SA Name</b></td>
                  <td>{ eachDevice.sa_name }</td>
                </tr>
                <tr>
                  <td><b>Domain</b></td>
                  <td>{ eachDevice.domain }</td>
                </tr>
                <tr>
                  <td><b>VA Name</b></td>
                  <td>{ eachDevice.va_name }</td>
                </tr>
              </tbody>
              </table>
            </ReactTooltip>
            </td>
            <td>{ eachDevice.s2Status }</td>
            <td>{ eachDevice.s3Status }</td>
          </tr>
        )
      }
    ) : (
      <tr>
        <th colSpan="6" className="text-nowrap font-weight-normal text-center"><img
          src={ loadingImage } alt="Loading ..."/></th>
      </tr>
    );


    return (
      <div>
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item " aria-current="page">Home</li>
              <li className="breadcrumb-item active" aria-current="page"> SLR Step 4: Applying Auth
                Key on Devices
                Devices
              </li>
            </ol>
          </nav>
        </div>

        <div className="container">
          <div className="slrInfo" onClick={this.infodivclickS4}>
            <a id="slrinfoPopuplink" href="#click">
            <i data-tip data-for="slrInfo" className="fa fa-info-circle text-primary"></i>
            <ReactTooltip className='opaque' id="slrInfo" type='light'>Click here for SLR Infomation</ReactTooltip>
            </a>
          </div>
          <div className="stepper" >
            <Stepper steps=
                       { [
                         { title: 'Device Details Upload' },
                         { title: 'Generating Request Code' },
                         { title: 'Getting Auth Code from CSSM' },
                         { title: '' }
                       ] }
                     activeStep={ 3 }
                     activeColor="#007bff"
                     completeColor="#28a745"
            />
          </div>
          <div className="gridDisplay">
            <div className="gridDisplay">
              <section>
                <div className="card">
                  <div className="card-header">
                    <h4>SLR Step 4: Applying Authorization Codes on Devices</h4>
                  </div>
                  <div className="card-body">
                    <p className="card-text"></p>
                    <div className="text-center">
                      <table className="table table-bordered table-sm table-hover slrTable">
                        <thead>
                        <tr>
                          <th className="text-nowrap text-center">Device IP</th>
                          <th className="text-nowrap text-center">Request Code Status</th>
                          <th className="text-nowrap text-center">Get Auth Code Status</th>
                        </tr>
                        </thead>
                        <tbody>
                        { deviceList }
                        </tbody>
                      </table>
                    </div>

                    <div className="text-left">
                      <Panel>
                        <Panel.Body className="">
                         <p>
                          <div className="stepMessageWarningContainer">
                            <div className="stepMessageWarning">
                              <div className="slrStepIcon">
                                <i className="fa fa-exclamation-triangle text-warning"></i>
                              </div>
                              <div className="slrStepWarningDescription">
                                  This step should be executed again on the network where the devices are connected and reachable
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
                                Click on <b>'Apply Authorization Codes'</b> to initiate this step
                              </div>
                            </div>
                          </div>
                         </p> 
                        </Panel.Body>
                      </Panel>
                    </div>
                    <div className="actionButtonGroup3">
                      <button className="btn btn-primary" onClick={ () => this.props.history.push('/') } > Home </button>
                      <UltimatePaginationBootstrap
                        className="customPagination"
                        totalPages={ this.state.totalPages }
                        currentPage={ this.state.page }
                        onChange={ this.onPageChange }
                      />
                      <button className="btn btn-primary"
                              onClick={ this.handleApplyAuthKeysClick }
                              disabled={ !this.state.isEnableButton }
                      >Apply Authorization Codes
                      </button>
                    </div>
                  </div>
                </div>

              </section>
            </div>
          </div>
        </div>

        { /*Modal Div*/ }
        <div>
          <Modal visible={ this.state.alertModal } className="transparentModal spinnerModal">
            <div className="modal-body">
              <div className="loader"></div>
            </div>
          </Modal>
        </div>        
        { /*End Of Modal*/ }
        {this.state.showSlrInfoPopupS4 ? <SlrStepsInfoPopup closeSlrInfo={this.closeSlrInfoPopupS4.bind(this)}/> : null}
      </div>
    )
  }
}

const mapStateToProps = state => ({
  register: state.register,
  auth: state.auth,
  alert: state.alert,
  uuid: state.common.uuid,
});

const connectedSlrStep4ApplyAuthKeys = connect(mapStateToProps)(SlrStep4ApplyAuthKeys);
export { connectedSlrStep4ApplyAuthKeys as SlrStep4ApplyAuthKeys };
