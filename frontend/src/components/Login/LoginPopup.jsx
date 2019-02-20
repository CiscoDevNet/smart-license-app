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
import { authAction } from '../../actions';
import { Button } from "react-bootstrap";

class LoginPopup extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      username: '',
      password: '',
      submitted: false
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(e) {
    const { name, value } = e.target;
    this.setState({ [name]: value });
  }

  handleSubmit(e) {
    e.preventDefault();

    let callAfterLoggedin = this.props.callAfterLogin;

    this.setState({ submitted: true });
    const { username, password } = this.state;
    const { dispatch } = this.props;

    if (username && password) {
      dispatch(authAction.login(username, password, callAfterLoggedin));
    }
    console.log("Login clicked !!");
  }

  render() {
    const { loggingIn } = this.props;
    const { username, password, submitted } = this.state;
    return (

        <div className='loginPopup'>
          <div className='loginPopupInner'>
            <div className="loginPopupClose">
              <Button onClick={ this.props.closeLoginPopup }><span aria-hidden="true">X</span></Button>
            </div>

            <div className="container">
                <div>
                    <h5>Login</h5>
                </div>
                <div className="loginSection">
                    <div>
                        <p>Login is required to connect to CSSM.</p>
                    </div>
                    <form name="form" onSubmit={ this.handleSubmit }>
                    <div className={ 'form-group' + (submitted && !username ? ' has-error' : '') }>
                        <div className="input-group mb-3">
                        <div className="input-group-prepend">
                            <span className="input-group-text" id="basic-addon1">
                            <i className="fa fa-user"></i>
                            </span>
                        </div>
                        <input type="text" className="form-control" placeholder="Username"
                                onChange={ this.handleChange } aria-label="Username"
                                aria-describedby="basic-addon1" name="username" value={ username }/>
                        </div>

                        { submitted && !username &&
                        <div className="help-block text-danger">Username is required</div>
                        }

                    </div>
                    <div className={ 'form-group' + (submitted && !password ? ' has-error' : '') }>
                        <div className="input-group mb-3">
                        <div className="input-group-prepend">
                            <span className="input-group-text" id="basic-addon1">
                            <i className="fa fa-eye-slash"></i>
                            </span>
                        </div>
                        <input type="password" className="form-control" placeholder="Password"
                                onChange={ this.handleChange } aria-label="Password"
                                aria-describedby="basic-addon1" name="password" value={ password }/>
                        </div>
                        { submitted && !password &&
                        <div className="help-block text-danger">Password is required</div>
                        }
                    </div>
                    <div className="form-group text-center">
                        <button className="btn btn-primary">Login</button>
                        { loggingIn &&
                        <img alt=""
                            src="data:image/gif;base64,R0lGODlhEAAQAPIAAP///wAAAMLCwkJCQgAAAGJiYoKCgpKSkiH/C05FVFNDQVBFMi4wAwEAAAAh/hpDcmVhdGVkIHdpdGggYWpheGxvYWQuaW5mbwAh+QQJCgAAACwAAAAAEAAQAAADMwi63P4wyklrE2MIOggZnAdOmGYJRbExwroUmcG2LmDEwnHQLVsYOd2mBzkYDAdKa+dIAAAh+QQJCgAAACwAAAAAEAAQAAADNAi63P5OjCEgG4QMu7DmikRxQlFUYDEZIGBMRVsaqHwctXXf7WEYB4Ag1xjihkMZsiUkKhIAIfkECQoAAAAsAAAAABAAEAAAAzYIujIjK8pByJDMlFYvBoVjHA70GU7xSUJhmKtwHPAKzLO9HMaoKwJZ7Rf8AYPDDzKpZBqfvwQAIfkECQoAAAAsAAAAABAAEAAAAzMIumIlK8oyhpHsnFZfhYumCYUhDAQxRIdhHBGqRoKw0R8DYlJd8z0fMDgsGo/IpHI5TAAAIfkECQoAAAAsAAAAABAAEAAAAzIIunInK0rnZBTwGPNMgQwmdsNgXGJUlIWEuR5oWUIpz8pAEAMe6TwfwyYsGo/IpFKSAAAh+QQJCgAAACwAAAAAEAAQAAADMwi6IMKQORfjdOe82p4wGccc4CEuQradylesojEMBgsUc2G7sDX3lQGBMLAJibufbSlKAAAh+QQJCgAAACwAAAAAEAAQAAADMgi63P7wCRHZnFVdmgHu2nFwlWCI3WGc3TSWhUFGxTAUkGCbtgENBMJAEJsxgMLWzpEAACH5BAkKAAAALAAAAAAQABAAAAMyCLrc/jDKSatlQtScKdceCAjDII7HcQ4EMTCpyrCuUBjCYRgHVtqlAiB1YhiCnlsRkAAAOwAAAAAAAAAAAA=="/>
                        }
                    </div>
                    <div>
                        If you don't have a Cisco.com account, you can register to get one, click <a
                        href="https://idreg.cloudapps.cisco.com/idreg/guestRegistration.do">here</a> to
                        register an account.
                    </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    );
  }
}

function mapStateToProps(state) {
  const { loggingIn } = state.auth;
  return {
    loggingIn
  };
}

const connectedLogin = connect(mapStateToProps)(LoginPopup);
export { connectedLogin as LoginPopup };