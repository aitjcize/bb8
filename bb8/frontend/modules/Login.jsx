import React from 'react'
import { Link } from 'react-router'

import { Card } from 'material-ui/Card'

import LoginForm from '../components/forms/LoginForm'
import Notification from '../components/Notification'
import LogoPNG from '../assets/logo.png'

const Login = () => (
  <Card className="b-login-card">
    <Notification />
    <div className="b-login-card__container">
      <span className="b-login-card__title"> Login </span>
      <img className="b-login-card__logo" src={LogoPNG} alt="logo" />
      <LoginForm />
      <div className="b-login-card__bottom">
        Do not have account yet? go to
        <Link to="/signup" > Signup </Link>
      </div>
    </div>
  </Card>
)

export default Login
