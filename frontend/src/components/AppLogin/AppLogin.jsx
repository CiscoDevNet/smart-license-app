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
import {loginAction} from '../../actions';
import { Link } from 'react-router-dom';

class AppLogin extends React.Component {
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

    handleChange(event) {
       const { name, value } = event.target;
       this.setState({ [name]: value });
    }

    handleSubmit(event) {
        event.preventDefault();
        this.setState({ submitted: true });
        const { username, password } = this.state;
        const { dispatch } = this.props;
        if (username && password) {
            dispatch(loginAction.login(username, password));
        }
        console.log("Logging in to the App")
    }

    render() {
    const {username,password,submitted} = this.state;
    const { appLogging } = this.props
    return (
        <div className='container'>
            <div class="row justify-content-center">
                <div class='col-md-4 col-md-offset-3'>
                    <br/><br/>
                    <h3> Login </h3>
                    <form name="form" onSubmit={this.handleSubmit}>
                        <div className={'form-group' + (submitted && !username ? ' has-error' : '')}>
                                    <label htmlFor="username">Username</label>
                                    <input type="text" className="form-control" name="username"
                                    value={username} onChange={this.handleChange} />
                                    {submitted && !username &&
                                        <div className="help-block text-danger">Username is required</div>
                                    }
                        </div>
                        <div className={'form-group' + (submitted && !password ? ' has-error' : '')}>
                                    <label htmlFor="password">Password</label>
                                    <input type="password" className="form-control" name="password"
                                    value={password} onChange={this.handleChange} />
                                    {submitted && !password &&
                                        <div className="help-block text-danger">Password is required</div>
                                    }
                        </div>
                        <div className="form-group">
                                <button className="btn btn-primary btn-block">Login</button>
                                { appLogging &&
                                <img alt=""
                                    src="data:image/gif;base64,R0lGODlhEAAQAPIAAP///wAAAMLCwkJCQgAAAGJiYoKCgpKSkiH/C05FVFNDQVBFMi4wAwEAAAAh/hpDcmVhdGVkIHdpdGggYWpheGxvYWQuaW5mbwAh+QQJCgAAACwAAAAAEAAQAAADMwi63P4wyklrE2MIOggZnAdOmGYJRbExwroUmcG2LmDEwnHQLVsYOd2mBzkYDAdKa+dIAAAh+QQJCgAAACwAAAAAEAAQAAADNAi63P5OjCEgG4QMu7DmikRxQlFUYDEZIGBMRVsaqHwctXXf7WEYB4Ag1xjihkMZsiUkKhIAIfkECQoAAAAsAAAAABAAEAAAAzYIujIjK8pByJDMlFYvBoVjHA70GU7xSUJhmKtwHPAKzLO9HMaoKwJZ7Rf8AYPDDzKpZBqfvwQAIfkECQoAAAAsAAAAABAAEAAAAzMIumIlK8oyhpHsnFZfhYumCYUhDAQxRIdhHBGqRoKw0R8DYlJd8z0fMDgsGo/IpHI5TAAAIfkECQoAAAAsAAAAABAAEAAAAzIIunInK0rnZBTwGPNMgQwmdsNgXGJUlIWEuR5oWUIpz8pAEAMe6TwfwyYsGo/IpFKSAAAh+QQJCgAAACwAAAAAEAAQAAADMwi6IMKQORfjdOe82p4wGccc4CEuQradylesojEMBgsUc2G7sDX3lQGBMLAJibufbSlKAAAh+QQJCgAAACwAAAAAEAAQAAADMgi63P7wCRHZnFVdmgHu2nFwlWCI3WGc3TSWhUFGxTAUkGCbtgENBMJAEJsxgMLWzpEAACH5BAkKAAAALAAAAAAQABAAAAMyCLrc/jDKSatlQtScKdceCAjDII7HcQ4EMTCpyrCuUBjCYRgHVtqlAiB1YhiCnlsRkAAAOwAAAAAAAAAAAA=="/>
                                }
                                <center>
                                    <Link to="/ForgotPassword" className="btn btn-link">Forgot Password</Link>
                                    <Link to="/Register" className="btn btn-link">Register</Link>
                                </center>
                         </div>
                    </form>
                </div>
             </div>
        </div>
    );
  }
}

function mapStateToProps(state) {
  const { appLogging } = state.appLogin;
  return {
    appLogging
  };
}

const connectedAppLogin = connect(mapStateToProps)(AppLogin);
export { connectedAppLogin as AppLogin };