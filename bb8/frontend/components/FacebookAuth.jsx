import React from 'react'
import { connect } from 'react-redux'

import FlatButton from 'material-ui/FlatButton'

import { startfacebookAuth } from '../actions/accountActionCreators'

const FacebookAuth = props =>
  <FlatButton
    onClick={() => props.dispatch(startfacebookAuth())}
  >
    Facebook Login
  </FlatButton>

FacebookAuth.propTypes = {
  dispatch: React.PropTypes.func,
}

const ConnectedFacebookAuth = connect()(FacebookAuth)

export default ConnectedFacebookAuth
