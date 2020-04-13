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
import { Router, Route } from 'react-router-dom';
import { connect } from 'react-redux';
import { history } from '../../helpers/history';
import { AppLogin } from '../AppLogin';
import { ForgotPassword } from '../ForgotPassword';
import { Register }  from '../Register';
import { Home } from '../Home';
import { Upload }  from '../Upload';
import { UploadedDevices }  from '../UploadedDevices';
import { RegistrationStatus } from '../RegistrationStatus/RegistrationStatus';
import { SlrStep1Upload } from '../SlrStep1Upload';
import { SlrStep2ReqCode } from '../SlrStep2ReqCode';
import { SlrStep2ReqCodeStatus } from '../SlrStep2ReqCodeStatus';
import { SlrStep3GetAuthKeys } from '../SlrStep3GetAuthKeys';
import { SlrStep3GetAuthKeysStatus } from '../SlrStep3GetAuthKeysStatus';
import { SlrStep4ApplyAuthKeys } from '../SlrStep4ApplyAuthKeys';
import { SlrStep4ApplyAuthKeysStatus } from '../SlrStep4ApplyAuthKeysStatus';
import { SlrImport } from '../SlrImport';
import { ToastContainer, toast } from 'react-toastify';
import 'font-awesome/css/font-awesome.min.css';
import '../../resources/css/common.css';
import '../../resources/css/index.css';

class App extends React.Component {

  showError(message,type){
    if(message){
      toast(() => {
        return (
          <div className="toasterDiv">
            <div className="icon">
              <i className={ type === "alert-success" ? 'fa fa-check fa-3x' : 'fa fa-exclamation-triangle fa-3x text-danger'}></i>
            </div>
            <div className="errorMessage">{message}</div>
          </div>
        )
      },{autoClose: false}
      );
    }
  }

  render() {
    const { alert } = this.props;
    return (
      <div>
        {this.showError(alert.message,alert.type) }
        <ToastContainer position="bottom-right" />
        <Router history={history}>
          <div>
            <Route exact path="/appLogin" component={AppLogin} />
            <Route exact path="/forgotPassword" component={ForgotPassword} />
            <Route exact path="/register" component={Register} />
            <Route exact path="/home" component={Home} />
            <Route exact path="/upload" component={Upload} />
            <Route exact path="/uploadedDevices" component={UploadedDevices} />
            <Route exact path="/registrationStatus" component={RegistrationStatus} />
            <Route exact path="/slrStep1Upload" component={SlrStep1Upload} />
            <Route exact path="/SlrStep2ReqCode" component={SlrStep2ReqCode} />
            <Route exact path="/slrStep2ReqCodeStatus" component={SlrStep2ReqCodeStatus} />
            <Route exact path="/slrStep3GetAuthKeys" component={SlrStep3GetAuthKeys} />
            <Route exact path="/slrStep3GetAuthKeysStatus" component={SlrStep3GetAuthKeysStatus} />
            <Route exact path="/slrStep4ApplyAuthKeys" component={SlrStep4ApplyAuthKeys} />
            <Route exact path="/slrStep4ApplyAuthKeysStatus" component={SlrStep4ApplyAuthKeysStatus} />
            <Route exact path="/slrImport" component={SlrImport} />
            <Route exact path="/" component={AppLogin} />
          </div>
        </Router>
      </div>
  );
  }
}

function mapStateToProps(state) {
  const { alert } = state;
  return {
      alert
  };
}

const connectedApp = connect(mapStateToProps)(App);
export { connectedApp as App };
