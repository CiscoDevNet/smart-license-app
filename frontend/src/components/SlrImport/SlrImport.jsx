import React from 'react';
import { connect } from 'react-redux';
import { Button } from "react-bootstrap";
import { commonAction } from '../../actions';
import '../../resources/css/Upload.css';
import axios from 'axios';
import { toaster } from "../../helpers/toasterHelper";
import Modal from 'react-bootstrap4-modal';
import { LoginPopup } from "../Login/LoginPopup";
import { getAuthToken, needsLoginCheck } from "../../helpers/serviceHelper";
import FileSaver from 'file-saver';
import { commonConstants } from "../../constants/common-constants";
import { getRegistrationStatus } from "../../helpers";
import { slrConstant } from "../../constants/slr-constants";
import { Panel } from "react-bootstrap";


const STATUS_SLR_IMPORT_START     = 0;
const STATUS_SLR_IMPORT_COMPLETED_REQ_CODE = 11;
const STATUS_SLR_IMPORT_COMPLETED_AUTH_KEY = 12;
const STATUS_SLR_IMPORT_ERROR     = 2;

const STATUS_SLR_IMPORT_GET_AUTH_KEY_IN_PROGRESS  = 31;
const STATUS_SLR_IMPORT_GET_AUTH_KEY_COMPLETED    = 32;

class SlrImport extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            slrImportFileSelected: null,
            slrImportLoaded: 0,
            uuid: null,
            alertModal: false,
            slrImportStatus: STATUS_SLR_IMPORT_START,
            slrImportFailureReason: 'Unknown',
            slrImportGetAuthCodeDevProcessed: 0,
            slrImportGetAuthCodeDevTotal: 0,
            showLoginPopup: false
        };
        this.handleSlrImportClick = this.handleSlrImportClick.bind(this);
        this.handleSlrImportCancelClick = this.handleSlrImportCancelClick.bind(this);
        this.hideLoadingModal = this.hideLoadingModal.bind(this);
        this.showLoadingModal = this.showLoadingModal.bind(this);
        this.handleSlrImportHomeClick = this.handleSlrImportHomeClick.bind(this);
        this.handleSlrImportGetAuthKeyClick = this.handleSlrImportGetAuthKeyClick.bind(this);
        this.handleSlrImportGetAuthKeyRefreshClick = this.handleSlrImportGetAuthKeyRefreshClick.bind(this);
        this.handleSlrImportAuthKeyContinueClick = this.handleSlrImportAuthKeyContinueClick.bind(this);
        this.handleSlrImportExportAuthCodesClick = this.handleSlrImportExportAuthCodesClick.bind(this);
    }

    handleSlrImportFileSelected = event => {
        this.setState({
            slrImportFileSelected: event.target.files[0] || null, slrImportLoaded: 0
        })
    }

    async componentWillMount() {
        const uuid = this.props.common.uuid;
        console.log('SLR Import, UUID: ' + uuid);
        if (typeof uuid !== 'undefined' && uuid !== '') {
            let regStatus = '-'; 
            const respObj = await getRegistrationStatus(uuid);
            const resp = await respObj.json();
            const actualResp = {
            ...resp,
            status: respObj.status,
            };
        
            if (actualResp.status === 200 || actualResp.status === 201) {
                regStatus = resp.status;
            } else {
                console.log('Need to handle error!');
                toaster(actualResp.status, actualResp.message);
            }
            console.log('SLR Import - uuid: ' + uuid + ', Reg Status: ' + regStatus)
            regStatus = regStatus.toLowerCase()

            if (regStatus === slrConstant.SLR_STEP_2_IMPORT_COMPLETED.toLowerCase()) {
                console.log('SLR Import: Req Codes Import Completed.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_COMPLETED_REQ_CODE
                });
            } else if (regStatus === slrConstant.SLR_STEP_3_IMPORT_COMPLETED.toLowerCase()) {
                console.log('SLR Import: Auth Codes Import Completed.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_COMPLETED_AUTH_KEY
                });
            } else if (regStatus === slrConstant.SLR_STEP_3_EXPORT_COMPLETED.toLowerCase()) {
                console.log('SLR Import: Auth Codes Export Completed.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_GET_AUTH_KEY_COMPLETED
                });
            } else if (regStatus === slrConstant.SLR_STEP_2_IMPORT_FAILED.toLowerCase()) {
                console.log('SLR Import: Request Codes Import Failed.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_ERROR,
                    slrImportFailureReason: 'Request Codes Import Failed.'
                });
            } else if (regStatus === slrConstant.SLR_STEP_3_IMPORT_FAILED.toLowerCase()) {
                console.log('SLR Import: Authorization Codes Import Failed.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_ERROR,
                    slrImportFailureReason: 'Authorization Codes Import Failed.'
                });
            } else if (regStatus === slrConstant.SLR_STEP_3_EXPORT_FAILED.toLowerCase()) {
                console.log('SLR Import:Authorization Codes Export Failed.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_ERROR,
                    slrImportFailureReason: 'Authorization Codes Export Failed.'
                });
            } else {
                console.log('SLR Import: Unknown Error.');
                this.setState({
                    uuid: uuid,
                    slrImportStatus: STATUS_SLR_IMPORT_ERROR,
                    slrImportFailureReason: 'Unknown Error.'
                });
            }
        }
    }
    

    handleSlrImportClick(event) {
        event.preventDefault();    
        this.setState({ submitted: true });
        const { slrImportFileSelected } = this.state;
        const { dispatch } = this.props;
        if (slrImportFileSelected) {
            console.log('SLR Import File: ' + slrImportFileSelected.name);
            this.handleFileImportSendToServer(slrImportFileSelected)
                .then(
                    importRsp => {
                        console.log({ importRsp });
                        let responseMessage = importRsp.message;
                        const responseImportUuid = importRsp.uuid;
                        const responseImportType = importRsp.codes_type;
                        this.setState({
                            uuid: responseImportUuid
                        });
                        console.log('Import UUID:' + responseImportUuid + ', Type: ' + responseImportType);
                        if ("File successfully uploaded!" === responseMessage) {
                            if ("request_codes" === responseImportType) {
                                console.log('Req Codes Imported');
                                this.setState({
                                    slrImportStatus: STATUS_SLR_IMPORT_COMPLETED_REQ_CODE
                                });

                            } else if ("auth_codes" === responseImportType) {
                                console.log('Authorization Codes Imported');
                                this.setState({
                                    slrImportStatus: STATUS_SLR_IMPORT_COMPLETED_AUTH_KEY
                                });
                            } else {
                                console.log('An error: Invalid type - ' + responseImportType);
                                this.setState({
                                    slrImportStatus: STATUS_SLR_IMPORT_ERROR,
                                    slrImportFailureReason: 'An error: Invalid type - ' + responseImportType
                                });
                            }
                        } else {
                            console.log('An error: ' + responseMessage);
                            if ('Registration request with this UUID already exists!' === responseMessage) {
                                responseMessage = 'Registration exists, importing file where it is exported from is not allowed or file import is allowed only once.'
                            } else if ('Registration request with this UUID doesn\'t exists!' === responseMessage) {
                                responseMessage = 'Registration not found or doesn\'t exist.'
                            } else if ('No File in the request!' === responseMessage || 'No File selected!' === responseMessage ) {
                                responseMessage = 'Importing file is missing.'
                            } else if ( 'File type not allowed! Only JSON files are allowed!' === responseMessage) {
                                responseMessage = 'Invalid file type. File should be of JSON type.'
                            } else if ('Reading file and decoding JSON has failed. Please check your JSON file syntax!' === responseMessage) {
                                responseMessage = 'Malformed JSON file, not a valid exported file.'
                            }
                            this.setState({
                                slrImportStatus: STATUS_SLR_IMPORT_ERROR,
                                slrImportFailureReason: responseMessage
                            });
                        }
                    },
                    error => {
                        dispatch(
                            toaster(error.toString())
                            //alertAction.error(error.toString())
                        );
                    }
                );
        }
      }

      handleFileImportSendToServer(file) {
        this.showLoadingModal();
        console.log('SLR JSON File Import - File:' + file.name);
        const data = new FormData()
        data.append('file', file, file.name);
        data.append('oauth_token', 'x')
        return axios.post(`/slr/importcodes`, data)
        .then(this.handleFileImportSendToServerResponse)
        .then(slrImportResponse => {
            console.log('importRsp:' + JSON.stringify(slrImportResponse));
            if(slrImportResponse.uuid) {
                localStorage.setItem('slrImportRsp', JSON.stringify(slrImportResponse));
            }
            this.hideLoadingModal();
            return slrImportResponse;
        });
    }
    
    handleFileImportSendToServerResponse(response) {
        console.log("Handle SLR Import Resp !!" + JSON.stringify(response))
    
        if (response.error) {
            console.log("Handle SLR Import Resp - No ERROR");
            return Promise.reject(response.error);
        }
        console.log("Handle SLR Import Resp - No ERROR");
    
        if (response.data) {
            const data = response.data;
            console.log('JSON.parse(data): ' + JSON.stringify(data))
            return data;
        }
    }
    
    handleSlrImportGetAuthKeyClick(event) {
        event.preventDefault();
        console.log('SLR Import GAK - UUID: ' + this.state.uuid);

        const userInfo = (this.props.auth.user);
        let needsLogin = needsLoginCheck(userInfo)
        //let needsLogin = true;
        if (needsLogin) {
          this.setState({ showLoginPopup: true });
        } else {
          console.log("SLR Import GAK Good To GO !!");
          this.handleGetAuthKeys();
        }
        console.log("Get Authorization Codes Clicked !!!");
    }

    async handleGetAuthKeys() {
        this.closeLoginPopup();
        this.showLoadingModal();
        const respObj = await this.getAuthKey();
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
            this.setState({
                slrImportStatus: STATUS_SLR_IMPORT_GET_AUTH_KEY_IN_PROGRESS,
            });
            this.refreshGetAuthKeyProgress();
        } else {
          console.log({ ...actualResp.status });
          toaster(actualResp.status, actualResp.message);
        }
    }
    
    getAuthKey() {
        const { auth } = this.props;
        const user = auth.user;
        const token = getAuthToken(user);
        //const token = "x";
        const url = `/device/cssm/authkey/${this.state.uuid}`;
    
        console.log('Get Authorization Codes - URL: ' +  url  + ', OAuth Token: ' + this.state.uuid);
        return fetch(url, {
          method: "POST",
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ oauth_token: token }),
        });
    }
    
    async refreshGetAuthKeyProgress() {
        let resObj = await this.fetchGAKstatus();
        console.log("11: " + resObj);
        const resp = await resObj.json();
        console.log("12: " + JSON.stringify(resp));
        const actualResp = {
          status: resObj.status,
          ...resp
        };
        console.log("13: " + actualResp );        
        if (actualResp.status === 200) {
            console.log("14: 200"); 
            const getAuthCodesStatus = actualResp.progress;
            console.log("150: Stat :: " + getAuthCodesStatus); 
            var stat = STATUS_SLR_IMPORT_GET_AUTH_KEY_IN_PROGRESS;
            if ("In-Progress" === getAuthCodesStatus) {
                stat = STATUS_SLR_IMPORT_GET_AUTH_KEY_IN_PROGRESS;
                console.log("151: Inp"); 
            } else if ("Completed" === getAuthCodesStatus) {
                stat = STATUS_SLR_IMPORT_GET_AUTH_KEY_COMPLETED;
                console.log("152: Com"); 
            } else {
                stat = STATUS_SLR_IMPORT_ERROR;
                console.log("153: err"); 
            }
            this.setState({
                slrImportStatus: stat,
                slrImportGetAuthCodeDevProcessed: actualResp.processed,
                slrImportGetAuthCodeDevTotal: actualResp.total
            });
        } else {
            console.log("17: err"); 
          console.log({ ...actualResp.status });
          toaster(actualResp.status, actualResp.message);
        }
        console.log("18: don"); 
    }

    fetchGAKstatus() {
        const url = `/slr/import/authcodes/status/${this.state.uuid}`;
        return fetch(url, {
            method: "GET",
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          });
    }

    handleSlrImportGetAuthKeyRefreshClick(event) {
        event.preventDefault(); 
        this.refreshGetAuthKeyProgress();    
    }

    handleSlrImportAuthKeyContinueClick(event) {
        event.preventDefault();    
        this.setState({ submitted: true });
        console.log('handleSlrImportAuthKeyContinueClick - uuid: ' + this.state.uuid);
        this.props.dispatch({
            type: commonConstants.SET_UUID,
            uuid: this.state.uuid,
          });
        commonAction.nextStep4();
    }

    handleSlrImportExportAuthCodesClick(event) {
        event.preventDefault();
        this.exportAuthCodesToAFile();
      }
    
      async exportAuthCodesToAFile() {
        console.log('calling exportAuthCodesToAFile:', this.state.uuid);
        this.showLoadingModal();
    
        const expAuthCodeRespObj = await fetch(`/slr/exportauthcodes/${this.state.uuid}`);
        const expAuthCodeResp = await expAuthCodeRespObj.json();
        const actualExpResp = {
          status: expAuthCodeRespObj.status,
          ...expAuthCodeResp,
        };
    
        console.log({ actualExpResp });
        this.hideLoadingModal();
    
        if (actualExpResp.status === 200) {
          console.log('ExpReqCodes: All Good!');
          console.log('JSON: ' + JSON.stringify(expAuthCodeResp));
          const regName = expAuthCodeResp["registration-name"];
          const fileName = 'authcodes-' + regName + '.json';
          const strippedFileName = fileName.replace('.csv', '');
          var blob = new Blob([JSON.stringify(expAuthCodeResp)], {type: "application/json;charset=utf-8"});
          FileSaver.saveAs(blob, strippedFileName);
    
        } else {
          console.log('ExpReqCodes: Need to handle error!');
          if (actualExpResp.status === 500) {
            toaster(actualExpResp.status, "Internal Error: Unable to export");
          } else if (actualExpResp.status === 404) {
            toaster(actualExpResp.status, "Error: No export found for the requested");
          } else {
            toaster(actualExpResp.status, "Unknown Error: Unable to export");
          }
        }    
    }

    handleSlrImportCancelClick(event) {
        event.preventDefault();    
        this.setState({ submitted: true });
        commonAction.cancelClicked();
    }

    showLoadingModal() {
        this.setState({ alertModal: true });
    }
    
    hideLoadingModal() {
        this.setState({ alertModal: false });
    }
    
    handleSlrImportHomeClick(event) {
        event.preventDefault();
        commonAction.goToHome();
    }

    closeLoginPopup() {
        this.setState( { showLoginPopup: false } )
    }


    render() {
        return (
            <div>
                <div>
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb">
                            <li className="breadcrumb-item " aria-current="page">Home</li>
                            <li className="breadcrumb-item active" aria-current="page">SLR Import</li>
                        </ol>
                    </nav>
                </div>
                <div className="container">
                    <section>
                        <h4>SLR Import</h4><hr/>
                    </section>

                    <div className="card">
                        <div className="card-body">
                            <div className="slrImportBody">

                                { this.state.slrImportStatus === STATUS_SLR_IMPORT_START &&
                                    <div id="slrimportcompleted">
                                        <div className="slrImportTitle">
                                            <div className="h5">File Import<hr/></div> 
                                            <p>Import a File that has Exported Request Codes or Authorization Codes.</p>
                                        </div>
                                        <div className="slrImportActions">
                                        <input type="file" accept="application/json" name="slrImportFile" id="slrImportFile"
                                                onChange={ this.handleSlrImportFileSelected }/>
                                        <Button className="btn btn-primary"
                                                onClick={ this.handleSlrImportClick }
                                                disabled={this.state.slrImportFileSelected === null}>Import</Button>
                                        <Button className="btn btn-primary" onClick={ this.handleSlrImportCancelClick }>Cancel</Button>
                                        </div>
                                    </div>
                                }
                                { this.state.slrImportStatus === STATUS_SLR_IMPORT_COMPLETED_REQ_CODE &&
                                    <div id="slrimportcompletedreq">
                                        <div className="h5">File Import - Request Codes<hr/></div>
                                        <div className="row ml-5 mr-5 mt-3 mb-3">
                                            <div className="col text"><strong>Status: </strong>Importing request codes is completed.</div>
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
                                                    Click on <b>'Get Authorization Codes'</b> to initiate this step
                                                </div>
                                                </div>
                                                <div className="stepMessageWarning">
                                                <div className="slrStepIcon">
                                                    <i className="fa fa-exclamation-triangle text-warning"></i>
                                                </div>
                                                <div className="slrStepWarningDescription">
                                                    This step should be executed on the network where Cisco Software Management(CSSM) API Server is reachable
                                                </div>
                                                </div>
                                                <div className="stepMessageWarning">
                                                <div className="slrStepIcon">
                                                    <i className="fa fa-exclamation-triangle text-warning"></i>
                                                </div>
                                                <div className="slrStepWarningDescription">
                                                    Make sure you are connected to the network which has connectivity to Internet and/or CSSM API Server
                                                </div>
                                                </div>
                                            </div>
                                            </p> 
                                            </Panel.Body>
                                        </Panel>
                                        </div>

                                        <div className="row text-center">
                                           <div className="col"><button className="btn btn-primary " onClick={ this.handleSlrImportHomeClick }>Home</button></div>
                                           <div className="col"><button className="btn btn-primary" onClick={ this.handleSlrImportGetAuthKeyClick } >Get Authorization Codes</button></div>
                                        </div>
                                    </div>
                                }
                                { this.state.slrImportStatus === STATUS_SLR_IMPORT_COMPLETED_AUTH_KEY &&
                                    <div id="slrimportcompletedauth">
                                        <div className="h5">File Import - Authorization Codes<hr/></div>
                                        <div className="row ml-5 mr-5 mt-3 mb-3">
                                            <div className="col text"><strong>Status: </strong>Importing Authorization Codes is Completed.</div>
                                        </div> 

                                        <div className="text-left">
                                            <Panel>
                                                <Panel.Body className="">
                                                <p>
                                                <div className="stepMessageSuccessContainer">
                                                    <div className="stepMessageWarning">
                                                    <div className="slrStepIcon">
                                                        <i className="fa fa-check-circle text-success"></i>
                                                    </div>
                                                    <div className="slrStepWarningDescription">
                                                         Ready to go to next step Applying  Authorization Codes
                                                    </div>
                                                    </div>
                                                    <div className="stepMessageWarning">
                                                    <div className="slrStepIcon">
                                                        <i className="fa fa-check-circle text-success"></i>
                                                    </div>
                                                    <div className="slrStepWarningDescription">
                                                        Click on <b>'Continue'</b> to perform the next step
                                                    </div>
                                                    </div>
                                                </div>
                                                </p> 
                                                </Panel.Body>
                                            </Panel>
                                        </div>

                                        <div className="row text-center">
                                           <div className="col"><button className="btn btn-primary " onClick={ this.handleSlrImportHomeClick }>Home</button></div>
                                           <div className="col"><button className="btn btn-primary" onClick={ this.handleSlrImportAuthKeyContinueClick } >Continue</button></div>
                                        </div>
                                    </div>
                                }
                                { this.state.slrImportStatus === STATUS_SLR_IMPORT_ERROR &&

                                    <div id="slrimporterror">
                                        <div className="h5">File Import - Failed<hr/></div>

                                        <div className="row ml-5 mr-5 mt-3 mb-3">
                                            <div className="col">
                                                <i className="fa fa-times-circle colorRed"></i> &nbsp;
                                                <strong>Reason:</strong> {this.state.slrImportFailureReason}
                                            </div>
                                        </div> 
                                        <div className="row ml-5 mr-5 mt-3 mb-3">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fix the error and try again</div>

                                        <div className="row text-center">
                                           <div className="col"><button className="btn btn-primary " onClick={ this.handleSlrImportHomeClick }>Home</button></div>
                                        </div>
                                    </div>
                                }

                                { this.state.slrImportStatus === STATUS_SLR_IMPORT_GET_AUTH_KEY_IN_PROGRESS &&
                                    <div id="slrimportcompletedauth">
                                        <div className="h5">File Import - Get Authorization Codes<hr/></div>
                                        <div className="row ml-5 mr-5 mt-3 mb-3">
                                            <div className="col text-center">
                                                <strong>Status: </strong>Getting Authorization Codes is in progress . . .&nbsp;&nbsp; {this.state.slrImportGetAuthCodeDevProcessed} of {this.state.slrImportGetAuthCodeDevTotal} &nbsp;&nbsp;
                                                <img alt="" style={{width: '30px', height: '30px'}} src="data:image/gif;base64,R0lGODlhEAAQAPIAAP///wAAAMLCwkJCQgAAAGJiYoKCgpKSkiH/C05FVFNDQVBFMi4wAwEAAAAh/hpDcmVhdGVkIHdpdGggYWpheGxvYWQuaW5mbwAh+QQJCgAAACwAAAAAEAAQAAADMwi63P4wyklrE2MIOggZnAdOmGYJRbExwroUmcG2LmDEwnHQLVsYOd2mBzkYDAdKa+dIAAAh+QQJCgAAACwAAAAAEAAQAAADNAi63P5OjCEgG4QMu7DmikRxQlFUYDEZIGBMRVsaqHwctXXf7WEYB4Ag1xjihkMZsiUkKhIAIfkECQoAAAAsAAAAABAAEAAAAzYIujIjK8pByJDMlFYvBoVjHA70GU7xSUJhmKtwHPAKzLO9HMaoKwJZ7Rf8AYPDDzKpZBqfvwQAIfkECQoAAAAsAAAAABAAEAAAAzMIumIlK8oyhpHsnFZfhYumCYUhDAQxRIdhHBGqRoKw0R8DYlJd8z0fMDgsGo/IpHI5TAAAIfkECQoAAAAsAAAAABAAEAAAAzIIunInK0rnZBTwGPNMgQwmdsNgXGJUlIWEuR5oWUIpz8pAEAMe6TwfwyYsGo/IpFKSAAAh+QQJCgAAACwAAAAAEAAQAAADMwi6IMKQORfjdOe82p4wGccc4CEuQradylesojEMBgsUc2G7sDX3lQGBMLAJibufbSlKAAAh+QQJCgAAACwAAAAAEAAQAAADMgi63P7wCRHZnFVdmgHu2nFwlWCI3WGc3TSWhUFGxTAUkGCbtgENBMJAEJsxgMLWzpEAACH5BAkKAAAALAAAAAAQABAAAAMyCLrc/jDKSatlQtScKdceCAjDII7HcQ4EMTCpyrCuUBjCYRgHVtqlAiB1YhiCnlsRkAAAOwAAAAAAAAAAAA=="/>
                                            </div>
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
                                                        Don't disconnect from the network
                                                    </div>
                                                    </div>
                                                    <div className="stepMessageWarning">
                                                    <div className="slrStepIcon">
                                                        <i className="fa fa-exclamation-triangle text-warning"></i>
                                                    </div>
                                                    <div className="slrStepWarningDescription">
                                                        Getting Authorization Codes from CSSM is in progress, wait until completed
                                                    </div>
                                                    </div>
                                                    <div className="stepMessageWarning">
                                                    <div className="slrStepIcon">
                                                        <i className="fa fa-exclamation-triangle text-warning"></i>
                                                    </div>
                                                    <div className="slrStepWarningDescription">
                                                        Click on <b>'Refresh'</b> to get the status updated
                                                    </div>
                                                    </div>
                                                </div>
                                                </p> 
                                                </Panel.Body>
                                            </Panel>
                                        </div>

                                        <div className="row text-center">
                                            <div className="col"><button className="btn btn-primary " onClick={ this.handleSlrImportHomeClick }>Home</button></div>
                                            <div className="col"><button className="btn btn-primary " onClick={ this.handleSlrImportGetAuthKeyRefreshClick  }>Refresh</button></div>
                                        </div>
                                    </div>
                                }

                                { this.state.slrImportStatus === STATUS_SLR_IMPORT_GET_AUTH_KEY_COMPLETED &&
                                    <div id="slrimportcompletedauth">
                                        <div className="h5">File Import - Get Authorization Codes<hr/></div>
                                        <div className="row ml-5 mr-5 mt-3 mb-3">
                                            <div className="col-8 text-left"><strong>Status: </strong>Getting Authorization Codes is completed.</div>
                                        </div>

                                        <div className="text-left">
                                            <Panel>
                                                <Panel.Body className="">
                                                <p>
                                                <div className="stepMessageWarningContainer">
                                                    <div className="stepMessageWarning">
                                                    <div className="slrStepIcon">
                                                        <i className="fa fa-check-circle text-success"></i>
                                                    </div>
                                                    <div className="slrStepWarningDescription">
                                                        Click on <b>'Export Authorization Codes'</b> to export the Authorization Codes to a file
                                                    </div>
                                                    </div>
                                                </div>
                                                </p> 
                                                </Panel.Body>
                                            </Panel>
                                        </div>
 
                                        <div className="row text-center">
                                           <div className="col"><button className="btn btn-primary " onClick={ this.handleSlrImportHomeClick }>Home</button></div>
                                           <div className="col"><button className="btn btn-primary" onClick={ this.handleSlrImportExportAuthCodesClick } >Export Authorization Codes</button></div>
                                        </div>
                                    </div>
                                }

                            </div>
                        </div>
                    </div>
                </div>

                { /*Modal Div*/ }
                <div>
                    <Modal visible={ this.state.alertModal } className="transparentModal spinnerModal">
                        <div className="modal-body"><div className="loader"></div></div>
                    </Modal>
                </div>
                { /*End Of Modal*/ }
                {this.state.showLoginPopup ? <LoginPopup closeLoginPopup={this.closeLoginPopup.bind(this)} 
                                                callAfterLogin={this.handleGetAuthKeys.bind(this)}  /> : null}
           </div>
        );
    }
}

function mapStateToProps(state) {
    const { slrImportFileSelected } = state;
    const { auth } = state;
    const { common } = state;
    const { status } = state;
    return { slrImportFileSelected, auth, common, status };
}

const connectedSlrImport =  connect(mapStateToProps)(SlrImport);
export { connectedSlrImport as SlrImport };