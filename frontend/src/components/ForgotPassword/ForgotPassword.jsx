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
import { Link } from 'react-router-dom';
import { passwordResetAction } from '../../actions'
import { passwordForgotAction } from '../../actions'

class ForgotPassword extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
           username : '',
           oldPassword: '',
           pswd_hint: '',
           newPassword: '',
           passwordCheck: false,
           disableAnswer: true,
           disableOldPassword : true,
           submitted: false
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
       const { name, value } = event.target;
       this.setState({ [name]: value });
       if (name === 'newPassword'){
            this.checkPassword();
       }
    }

     checkPassword(){
        const re = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
        if(re.test(this.state.newPassword))
        {
            this.setState({passwordCheck: true})
        }
        else{
            this.setState({passwordCheck: false })
        }
    }

    handleSubmit(event){
        event.preventDefault();
        this.setState({ submitted: true });
        const { username, oldPassword, pswd_hint, newPassword, passwordCheck } = this.state;
        const { dispatch } = this.props;
        if (username && oldPassword && newPassword && passwordCheck ) {
            dispatch(passwordResetAction.reset(username, oldPassword, newPassword));
        }
        if( username && pswd_hint && newPassword && passwordCheck ) {
            dispatch(passwordForgotAction.forgotPassword(username, pswd_hint, newPassword));
        }
        console.log("Updating the password")
    }

    disableAnswerFunc(){
         this.setState({ disableAnswer: true })
         this.setState({ disableOldPassword: false })
    }

    disableOldPasswordFunc(){
        this.setState({ disableAnswer: false })
        this.setState({ disableOldPassword: true })
    }

    render() {
        const { username, oldPassword, pswd_hint, newPassword, passwordCheck, submitted, disableAnswer,
        disableOldPassword } = this.state
        const { resetPassword } = this.props;
        return (
            <div className='container'>
                <div class="row justify-content-center">
                    <div class='col-md-4 col-md-offset-3'>
                        <br/><br/>
                        <h3> Forgot Password </h3>
                        <form name="form" onSubmit={this.handleSubmit}>
                            <div className={'form-group' + (submitted && !username ? ' has-error' : '')}>
                                <label htmlFor="username"> Username </label>
                                <input type="text" className="form-control" name="username"
                                        value={username} onChange={ this.handleChange } />
                                {   submitted && !username &&
                                        <div className="help-block text-danger"> Username is required</div>
                                }
                            </div>
                            <div className="form-check">
                              <label>
                                <input type="radio" name="resetPassword" value="Old Password"
                                className="form-check-input" onClick = { this.disableAnswerFunc.bind(this) }
                                />
                                Please type your old password
                              </label>
                              <input type="password" className="form-control" name="oldPassword"
                                    value={oldPassword} onChange={this.handleChange} disabled = {this.state
                                    .disableOldPassword }/>
                              {  submitted && !oldPassword && !pswd_hint &&
                                        <div className="help-block text-danger"> Old password or hint answer is
                                        required</div>
                                }
                            </div>
                            <div className="form-check">
                              <label>
                                <input type="radio" name="resetPassword" value="Question"
                                  className="form-check-input" onClick = { this.disableOldPasswordFunc.bind(this) }
                                />
                                 Answer the hint question
                              </label>
                              <input type="text" className="form-control" name="pswd_hint"
                                    value={pswd_hint} onChange={this.handleChange} disabled = { this.state.disableAnswer }/>
                                 {  submitted && !oldPassword && !pswd_hint &&
                                        <div className="help-block text-danger">Old password or hint answer is
                                        required</div>
                                }
                            </div>
                            <div className={'form-group' + (submitted && !newPassword ? ' has-error' : '')}>
                                <label htmlFor="newPassword"> Please type new password</label>
                                <input type="password" className="form-control" name="newPassword"
                                        value={newPassword} onChange={ this.handleChange } />
                                <div style={{fontSize: '9px'}} > Use 8 or more alphanumeric characters with atleast
                                one capital and one special character </div>
                                {   (submitted && (!passwordCheck || !newPassword)) &&
                                        <div className="help-block text-danger"> New password is required and should
                                         follow the password rules</div>
                                }
                            </div>
                            <div className="form-group">
                                <button className="btn btn-primary">Reset Password</button>
                                { resetPassword }
                                <Link to="/AppLogin" className="btn btn-link">Cancel</Link>
                            </div>
                        </form>
                    </div>
                 </div>
            </div>
        );
      }
}

function mapStateToProps(state) {
  const { resetPassword } = state.forgotPassword;
  return {
    resetPassword
  };
}

const connectedForgotPassword = connect(mapStateToProps)(ForgotPassword);
export { connectedForgotPassword as ForgotPassword }
