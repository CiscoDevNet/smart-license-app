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
import Modal from 'react-bootstrap4-modal';
import { getAuthToken } from "../../helpers/serviceHelper";
import '../../resources/css/common.css';
import 'react-toastify/dist/ReactToastify.min.css';
import { toaster } from "../../helpers/toasterHelper";
import ReactTooltip from 'react-tooltip';
import { commonConstants } from "../../constants";

class RegistrationStatus extends Component {

  constructor(props) {
    super(props);
    this.state = {
      registeredDevices: [],
      page: 1,
      totalPages: 1,
      alertModal: false,
    };
    this.refreshRegisterStatus = this.refreshRegisterStatus.bind(this);
    this.onPageChange = this.onPageChange.bind(this);
    this.hideLoadingModal = this.hideLoadingModal.bind(this);
    this.showLoadingModal = this.showLoadingModal.bind(this);
  }

  async refreshRegisterStatus(page) {
    try {
      const pageNumber = typeof page === typeof 5 ? page : this.state.page;
      console.log('calling refreshRegisterStatus:', this.props);
      this.showLoadingModal();
      const uuid = this.props.register.uuid;
      const resp = await this.fetchRegisterStatus(`/sl/tokens/status/${ uuid }/${ pageNumber }`);
      const actualResp = await resp.json();

      this.hideLoadingModal();
      if (resp.status === 200 || resp.status === 201) {
        console.log({ resp });
        this.setState({
          registeredDevices: [...actualResp.devices],
          totalPages: actualResp.totalpages,
        })
      } else {
        toaster(resp.status, actualResp.message);
        throw new Error(actualResp.message);
      }

    } catch (error) {

    }

  }

  async componentWillMount() {
    await this.refreshRegisterStatus(1);
  }


  fetchRegisterStatus(url) {
    const user = (this.props.auth.user);
    const token = getAuthToken(user);
    return fetch(url, {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ oauth_token: token }),
    });
  }

  showLoadingModal() {
    this.setState({ alertModal: true });
  }

  hideLoadingModal() {
    this.setState({ alertModal: false });
    // this.setState({ alertModal: true });
  }

  async onPageChange(page) {
    console.log({ page });
    this.setState({ page });
    await this.refreshRegisterStatus(page);
  }

  componentWillUnmount() {
    this.props.dispatch({
      type: commonConstants.RESET_UUID,
    });
  }

  render() {
    const deviceList = this.state.registeredDevices !== null ? this.state.registeredDevices.map((eachDevice, index) => {

        return (
          <tr key={ `eachDevice.ipaddr:${ index }` }>
            <td>{ eachDevice.ipaddr }&nbsp;
              <i data-tip data-for={ eachDevice.ipaddr } className="fa fa-info-circle text-primary"></i>
              <ReactTooltip className='opaque' id={ eachDevice.ipaddr } type='light'>
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

            <td>{ eachDevice.sa_name }</td>
            <td>{ eachDevice.domain }</td>
            <td>{ eachDevice.va_name }</td>
            <td>{ eachDevice.status }</td>
          </tr>
        )
      }
    ) : (
      <tr>
        <th colSpan="6" className="text-nowrap font-weight-normal text-center">
          <div className="loader spinner"></div>
        </th>
      </tr>
    );


    return (
      <div>
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item " aria-current="page">Home</li>
              <li className="breadcrumb-item active" aria-current="page">Upload Devices /Register
                Devices
              </li>
            </ol>
          </nav>
        </div>

        {/*Container*/ }
        <div className="container">
          <div className="gridDisplay">
            <div className="gridDisplay">
              <section>
                <h4>Registration Status</h4>
                <hr/>
                <div className="card">
                  <div className="card-body">
                    <p className="card-text"></p>
                    <div className="text-center">
                      <table className="table table-bordered table-sm table-hover">
                        <thead>
                        <tr>
                          <th className="text-nowrap text-center">Device IP</th>
                          {/*<th className="text-nowrap text-center">User Name</th>*/ }
                          {/*<th className="text-nowrap text-center">Password</th>*/ }
                          <th className="text-nowrap text-center">Smart Account</th>
                          <th className="text-nowrap text-center">Smart Account Domain</th>
                          <th className="text-nowrap text-center">Virtual Account</th>
                          <th className="text-nowrap text-center">Status</th>
                        </tr>
                        </thead>
                        <tbody>
                        { deviceList }
                        </tbody>
                      </table>
                    </div>
                    <div className="actionButtonGroup3">
                      <button className="btn btn-primary"
                              onClick={ () => {
                                console.log('button Clicked!')
                                this.props.history.push('/')
                              }
                              }>Home
                      </button>
                      <UltimatePaginationBootstrap
                        className="customPagination"
                        totalPages={ this.state.totalPages }
                        currentPage={ this.state.page }
                        onChange={ this.onPageChange }
                      />
                      <button className="btn btn-primary"
                              onClick={ this.refreshRegisterStatus }>Refresh
                      </button>
                    </div>
                  </div>
                </div>

              </section>
            </div>
            { /*End of previousRegistration section*/ }
          </div>
        </div>

        {/*Modal*/ }
        <div>
          <Modal visible={ this.state.alertModal } className="transparentModal spinnerModal">
            <div className="modal-body">
              <div className="loader"></div>
            </div>
          </Modal>

        </div>


      </div>
    )
  }
}

const mapStateToProps = state => ({
  register: state.register,
  auth: state.auth,
  alert: state.alert,
});

const RegisteredDevice = connect(mapStateToProps)(RegistrationStatus);
export { RegisteredDevice as RegistrationStatus };
