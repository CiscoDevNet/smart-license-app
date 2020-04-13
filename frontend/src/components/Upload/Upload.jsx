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
import { Button } from "react-bootstrap";
import { uploadAction, commonAction } from '../../actions';
import '../../resources/css/Upload.css';

class Upload extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedFile: null,
      loaded: 0,
      uploadRsp: null,
      alertModal: false,
    };
    this.handleUpload = this.handleUpload.bind(this);
    this.handleCancelCick = this.handleCancelCick.bind(this);
  }

  showLoadingModal() {
    this.setState({ alertModal: true });
  }

  hideLoadingModal() {
    this.setState({ alertModal: false });
  }

  handleselectedFile = event => {

    this.setState({
      selectedFile: event.target.files[0] || null,
      loaded: 0
    })
  }

  handleUpload(event) {
    console.log('uploadClicked:', event.target);
    event.preventDefault();

    this.setState({ submitted: true });
    const { selectedFile } = this.state;
    const { dispatch } = this.props;
    if (selectedFile) {
      console.log('Selected File: ' + selectedFile.name);
      dispatch(uploadAction.upload(selectedFile, 'sl'));
    }
  }

  handleCancelCick(event) {
    event.preventDefault();
    commonAction.cancelClicked();
  }

  render() {
    console.log('Render called from:Upload');
    return (
      <div>
        <div className="container">
          <section>
           <h4>Device Details Upload</h4><hr/>
          </section>
          <div className="card">
            <div className="card-body">
              <div className="uploadBody">
                <div className="uploadTitle">
                  <p>Upload a CSV File that has the Smart Account, Virtual Account
                  and Device Details</p>
                </div>
                <div className="uploadActions">
                  <input type="file" accept="text/csv" name="devicesFile" id="devicesFile"
                         onChange={ this.handleselectedFile }/>
                  <Button className="btn btn-primary"
                          onClick={ this.handleUpload }
                          disabled={this.state.selectedFile === null}>Upload</Button>
                  <Button className="btn btn-primary" onClick={ this.handleCancelCick }>Cancel</Button>
                </div>
              </div>
            </div>
          </div>

          <div className="text-right">
            Click <a href="./SampleDevicesDetails.csv" download>here</a> to download a sample file
          </div>

        </div>

      </div>
    );
  }
}

function mapStateToProps(state) {
  const { uploadedFile, uploadRsp } = state;
  return {
    uploadedFile,
    uploadRsp
  };
}

const connectedUpload = connect(mapStateToProps)(Upload);
export { connectedUpload as Upload };
