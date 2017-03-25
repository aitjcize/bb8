import React from 'react'
import { connect } from 'react-redux'
import stylePropType from 'react-style-proptype'

import FlatButton from 'material-ui/FlatButton'

import { startfacebookAuth } from '../actions/accountActionCreators'
import FacebookIcon from '../assets/svgIcon/FacebookIcon'

const FacebookAuth = props =>
  <FlatButton
    onClick={() => props.dispatch(startfacebookAuth(props.inviteCode))}
    style={{ ...{
      backgroundColor: '#3B5998',
      color: 'white',
    },
      ...props.style }}
    icon={<FacebookIcon />}
    label={props.label || 'Login via Facebook'}
    labelPosition="after"
    labelStyle={{ textTransform: 'none' }}
  />

FacebookAuth.propTypes = {
  dispatch: React.PropTypes.func,
  style: stylePropType,
  label: React.PropTypes.string,
  inviteCode: React.PropTypes.string,
}

const ConnectedFacebookAuth = connect()(FacebookAuth)

export default ConnectedFacebookAuth
