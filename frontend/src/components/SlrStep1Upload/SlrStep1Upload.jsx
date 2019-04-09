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
import { uploadAction, commonAction } from '../../actions';
import { Button } from "react-bootstrap";
import Stepper from 'react-stepper-horizontal';
import ReactTooltip from 'react-tooltip';
import { SlrStepsInfoPopup } from '../SlrCommon/SlrStepsInfoPopup';

class SlrStep1Upload extends React.Component {
  constructor(props) {
    super(props);
    this.state = { selectedFile: null, loaded: 0, uploadRsp: null, showSlrInfoPopupS1: false }
    this.handleUpload = this.handleUpload.bind(this);
    this.handleCancelCick = this.handleCancelCick.bind(this);
    this.infodivclick = this.infodivclick.bind(this);
  }

  handleselectedFile = event => {
    this.setState({
      selectedFile: event.target.files[0],
      loaded: 0
    })
  }

  handleUpload(event) {
    event.preventDefault();

    this.setState({ submitted: true });
    const { selectedFile } = this.state;
    const { dispatch } = this.props;
    if (selectedFile) {

      console.log('Selected File: ' + selectedFile.name);
      dispatch(uploadAction.upload(selectedFile, 'slr'));


    }
  }

  handleCancelCick(event) {
    event.preventDefault();
    commonAction.cancelClicked();
  }

  infodivclick() {
    this.setState({showSlrInfoPopupS1: true});
  }

  closeSlrInfoPopup() {
    this.setState({ showSlrInfoPopupS1: false })
  }


  render() {
    return (
      <div>
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb">
              <li className="breadcrumb-item " aria-current="page">Home</li>
              <li className="breadcrumb-item active" aria-current="page">SLR Upload</li>
            </ol>
          </nav>
        </div>


        <div className="container">
          <div className="slrInfo" onClick={this.infodivclick}>
            <a id="slrinfoPopuplink" href="#click">
            <i data-tip data-for="slrInfo" className="fa fa-info-circle text-primary"></i>
            <ReactTooltip className='opaque' id="slrInfo" type='light'>Click here for SLR Infomation</ReactTooltip>
            </a>
          </div>
          <div className="stepper">
            <Stepper steps={ [
              { title: '' },
              { title: 'Generating Request Code' },
              { title: 'Getting Auth Code from CSSM' },
              { title: 'Applying Auth Code on Devices' }
            ] }
                     activeColor="#007bff"
                     activeStep={ 0 }/>
          </div>
          <div className="card">
            <div className="card-header">
              <h4>SLR Step 1: Device Details Upload</h4>
            </div>
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
                          disabled={ this.state.selectedFile === null }>Upload</Button>
                  <Button className="btn btn-primary"
                          onClick={ this.handleCancelCick }>Cancel</Button>
                </div>
              </div>
            </div>
          </div>

          <div className="text-right">
            Click <a href="./SampleDevicesDetails-SLR.csv" download>here</a> to download a sample file
          </div>

        </div>
        {this.state.showSlrInfoPopupS1 ? <SlrStepsInfoPopup closeSlrInfo={this.closeSlrInfoPopup.bind(this)}/> : null}
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

const connectedSlrStep1Upload = connect(mapStateToProps)(SlrStep1Upload);
export { connectedSlrStep1Upload as SlrStep1Upload };
