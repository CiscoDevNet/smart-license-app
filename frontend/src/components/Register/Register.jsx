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
import { userRegisterAction } from '../../actions'

class Register extends React.Component {
   constructor(props) {
        super(props);
        this.state = {
        user:{
               username: '',
               password: '',
               pswd_hint: ''
           },
           passwordCheck: false,
           submitted: false
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
       const { name, value } = event.target;
       const { user } = this.state;
       this.setState({
                user: {
                    ...user,
                    [name]: value
                }
            }, () => { if (name === 'password') {
             this.checkPassword(); }
       });
    }

    checkPassword(){
        const re = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
        if(re.test(this.state.user.password))
        {
            this.setState({passwordCheck: true})
        }
        else{
            this.setState({passwordCheck: false })
        }
    }

    handleSubmit(event) {
        event.preventDefault();
        this.setState({ submitted: true });
        const{user, passwordCheck} = this.state;
        if (user.username && user.password && user.pswd_hint && passwordCheck ) {
                    this.props.register(user);
        }
    }

    render() {
    const {user,submitted,passwordCheck} = this.state;
    const { registering } = this.props;
    console.log(passwordCheck)
    return (
        <div className='container'>
            <div class="row justify-content-center">
                <div class='col-md-4 col-md-offset-3'>
                    <br/><br/>
                    <h3> Register </h3>
                    <form name="form" onSubmit={this.handleSubmit}>
                        <div className={'form-group' + (submitted && !user.username ? ' has-error' : '')}>
                                    <label htmlFor="username">Username</label>
                                    <input type="text" className="form-control" name="username"
                                    value={user.username} onChange={this.handleChange} />
                                    {submitted && !user.username &&
                                        <div className="help-block text-danger">Username is required</div>
                                    }
                        </div>
                        <div className={'form-group' + ((submitted && (!passwordCheck || !user.password)) ? ' has-error' : '')}>
                                    <label htmlFor="password">Password</label>
                                    <input type="password" className="form-control" name="password"
                                    value={user.password} onChange={this.handleChange} />
                                    <div style={{fontSize: '9px'}} > Use 8 or more alphanumeric characters with atleast one capital and one special character </div>
                                    {(submitted && (!passwordCheck || !user.password))  &&
                                        <div className="help-block text-danger">Password is required and should follow the password rules</div>}
                        </div>
                        <div className={'form-group' + (submitted && !user.pswd_hint ? ' has-error' : '')}>
                                    <label htmlFor="pswd_hint">Hint Question: What is your mother’s maiden name?</label>
                                    <input type="text" className="form-control" name="pswd_hint"
                                    value={user.pswd_hint} onChange={this.handleChange} />
                                    {submitted && !user.pswd_hint &&
                                        <div className="help-block text-danger">Please provide answer to the hint
                                        question</div>
                                    }
                        </div>
                        <div className="form-group">
                                <button className="btn btn-primary">Register</button>
                                {registering }
                                <Link to="/AppLogin" className="btn btn-link">Cancel</Link>
                         </div>
                    </form>
                </div>
            </div>
        </div>
    );
  }
}

function mapState(state) {
  const { registering } = state.registration;
  return {
    registering
  };
}

const actionCreators = {
    register: userRegisterAction.register
}

const connectedRegisterPage = connect(mapState, actionCreators)(Register);
export { connectedRegisterPage as Register };
