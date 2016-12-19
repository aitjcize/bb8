import React from 'react'
import { Link } from 'react-router'

import Paper from 'material-ui/Paper'

import LoginForm from '../components/forms/LoginForm'
import FacebookAuth from '../components/FacebookAuth'
import Notification from '../components/Notification'

const styles = {
  container: {
    height: '100vh',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginBox: {
    width: '25vw',
    minWidth: '30em',
    position: 'relative',
  },
  rows: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    margin: '1em 4vw',
  },
  loginForm: {
    alignSelf: 'stretch',
  },
  facebookAuthButton: {
    margin: '1.5em 0',
  },
  link: {
    color: '#1DE9B6',
    fontWeight: 'bold',
    padding: '0 .5em',
  },
  signupHint: {
    position: 'absolute',
    width: '100%',
    textAlign: 'center',
    fontSize: '.875em',
    margin: '.5em 0',
  },
}

const Login = () => (
  <div style={styles.container}>
    <Paper style={styles.loginBox}>
      <Notification />
      <div style={styles.rows}>
        <LoginForm style={styles.loginForm} />
      </div>
      <div style={styles.rows}>
        or
        <FacebookAuth style={styles.facebookAuthButton} />
      </div>
      <div style={styles.signupHint}>
        Do not have account yet?
        <Link to="/signup" style={styles.link} > Signup now </Link>
      </div>
    </Paper>
  </div>
)

export default Login
