import React from 'react'

import Paper from 'material-ui/Paper'
import Avatar from 'material-ui/Avatar'
import IconSwapHoriz from 'material-ui/svg-icons/action/swap-horiz'

import FacebookAuth from '../components/FacebookAuth'
import Notification from '../components/Notification'

import ComposeaiLogo from '../assets/logo.svg'

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
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-around',
    padding: '2vw',
  },
  facebookAuthButton: {
    marginRight: '2em',
  },
}

const Login = () => (
  <div style={styles.container}>
    <Paper style={styles.loginBox}>
      <Notification />
      <Avatar
        style={{
          backgroundImage: `url(${ComposeaiLogo})`,
          backgroundSize: '60%',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          width: '4em',
          height: '4em',
        }}
      />
      <IconSwapHoriz />
      <FacebookAuth style={styles.facebookAuthButton} />
    </Paper>
  </div>
)

export default Login
