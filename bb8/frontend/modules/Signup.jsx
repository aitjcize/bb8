import React from 'react'
import { Link } from 'react-router'

import { Card } from 'material-ui/Card'

import FacebookAuth from '../components/FacebookAuth'
import SignupForm from '../components/forms/SignupForm'
import LogoPNG from '../assets/logo.png'

const Signup = () => (
  <Card className="b-login-card">
    <div className="b-login-card__container">
      <span className="b-login-card__title"> Signup </span>
      <img className="b-login-card__logo" src={LogoPNG} alt="logo" />
      <SignupForm />
      <FacebookAuth />
      <div className="b-login-card__bottom">
        Already have the account? go to
        <Link to="/login" > Login </Link>
      </div>
    </div>
  </Card>
)

export default Signup
