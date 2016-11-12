import React from 'react'
import { connect } from 'react-redux'
import Snackbar from 'material-ui/Snackbar'

import { closeNotification } from '../actions'

const Notification = props => (
  <Snackbar
    open={props.open}
    message={props.message}
    autoHideDuration={3000}
    onRequestClose={() => props.dispatchClose()}
  />
)

Notification.propTypes = {
  open: React.PropTypes.bool,
  message: React.PropTypes.string,
  dispatchClose: React.PropTypes.func,
}

const ConnectedNotification = connect(
  state => ({
    open: state.notification.open,
    message: state.notification.message,
  }),
  dispatch => ({
    dispatchClose() {
      dispatch(closeNotification())
    },
  }),
)(Notification)

export default ConnectedNotification
