import React from 'react'
import { Link } from 'react-router'

import { Card } from 'material-ui/Card'

import FacebookAuth from '../components/FacebookAuth'
import Notification from '../components/Notification'
import LogoPNG from '../assets/logo.png'

const Signup = (data) => {
  const inviteCode = data.location.query.invite_code
  if (!inviteCode) {
    return (
      <Card className="b-login-card">
        <div className="b-login-card__container">
          <span className="b-login-card__title"> Signup </span>
          <img className="b-login-card__logo" src={LogoPNG} alt="logo" />
          <div className="b-login-card__bottom">
            We are currently in closed-beta, invitation only.
          </div>
        </div>
      </Card>
    )
  }
  return (
    <Card className="b-login-card">
      <Notification />
      <div className="b-login-card__container">
        <span className="b-login-card__title"> Signup </span>
        <img className="b-login-card__logo" src={LogoPNG} alt="logo" />
        <FacebookAuth label="Signup with Facebook" inviteCode={inviteCode} />
        <div className="b-login-card__bottom">
          Already have the account? go to
          <Link to="/login" > Login </Link>
        </div>
      </div>
    </Card>
  )
}

export default Signup
