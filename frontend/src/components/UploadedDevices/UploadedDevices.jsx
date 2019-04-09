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
import UltimatePaginationBootstrap from 'react-ultimate-pagination-bootstrap-4';
import { getAuthToken, needsLoginCheck } from '../../helpers/serviceHelper';
import { registerConstant } from "../../constants";
import {LoginPopup } from "../Login/LoginPopup";
import Modal from 'react-bootstrap4-modal';

const passwordMask = '********';

class UploadedDevices extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      devices: null,
      page: localStorage.getItem('page') ? localStorage.getItem('page') : 1,
      totalPages: (this.props && this.props.upload && this.props.upload.uploadRsp && this.props.upload.uploadRsp.totalpages) || 1,
      showLoginPopup: false,
      alertModal: false,
    };
    this.modalRef = null;
    this.modalMessage = '';
    this.handleRegisterClick = this.handleRegisterClick.bind(this);
    this.handleRegisterDevices = this.handleRegisterDevices.bind(this);
    this.onPageChange = this.onPageChange.bind(this);
  }

  componentWillMount() {
    this.fetchDevicePage(1);
    console.log("Total Pages:", this.state.totalPages);
  }

  handleRegisterClick() {
    const userInfo = (this.props.auth.user);
    let needsLogin = needsLoginCheck(userInfo)
    if (needsLogin) {
      this.setState({ showLoginPopup: true });
    } else {
      console.log("Good To GO !!");
      this.handleRegisterDevices();
    }
    console.log("Register Clicked !!!");
  }

  handleRegisterDevices() {
    console.log('In handleRegisterDevices');
    this.modalMessage = 'Initiating Registration....';
    console.log("Props:", { ...this.props });

    const user = (this.props.auth.user);
    let token = getAuthToken(user);

    const { uuid } = this.props.upload.uploadRsp;
    const { dispatch } = this.props;
    let uri = `/sl/tokens/${uuid}`;
    fetch(uri, {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ oauth_token: 'Bearer ' + token }),
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
    const { uploadRsp } = this.props.upload;
    let uuid = uploadRsp.uuid;
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

  closeLoginPopup() {
    this.setState( { showLoginPopup: false } )
  }

  render() {
    console.log('Render called from:UploadedDevices');
    let devices = this.state.devices;
    let devicesRows = <tr>
      <th colSpan="6" className="text-nowrap font-weight-normal text-center">
        <div className="loader"></div>
      </th>
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
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item " aria-current="page">Home</li>
              <li className="breadcrumb-item active" aria-current="page">Upload Devices</li>
            </ol>
          </nav>
        </div>

        <div className="container">
          <section>
            <h4> Device Details</h4><hr/>
          </section>
          <div className="card">
            <div className="card-body">

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
              <div className="actionButtonGroup3">
                <button className="btn btn-primary" onClick= {() => {this.props.history.push('/')}}>Cancel</button>
                <UltimatePaginationBootstrap
                  totalPages={ this.state.totalPages }
                  currentPage={ this.state.page }
                  onChange={ this.onPageChange }
                />
                <button className="btn btn-primary" onClick={ () => {
                  console.log('handle Click:handleRegisterDevices');
                  this.handleRegisterClick();
                } }>Register</button>
              </div>
            </div>
          </div>
        </div>
        { /*Modal Div*/ }
        <div>
          <Modal visible = {this.state.alertModal} className="transparentModal spinnerModal">
            <div className="modal-body">
              <div className="loader"></div>
            </div>
          </Modal>
        </div>
        { /*End Of Modal*/ }
        {this.state.showLoginPopup ? <LoginPopup closeLoginPopup={this.closeLoginPopup.bind(this)} 
                                                   callAfterLogin={this.handleRegisterDevices.bind(this)}  /> : null}
      </div>
    );
  }
}

function mapStateToProps(state) {
  const { alert, auth, upload } = state;
  return {
    alert,
    auth,
    upload
  }
}

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


const connectedUploadedDevices = connect(mapStateToProps)(UploadedDevices);
export { connectedUploadedDevices as UploadedDevices };
