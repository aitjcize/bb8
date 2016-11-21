import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'

import * as dialogActionCreators from '../../actions/dialogActionCreators'

const BroadcastSendDialog = (props) => {
  const actionCreators = bindActionCreators(
    dialogActionCreators, props.dispatch)

  const actions = [
    <FlatButton
      label="Cancel"
      primary
      onTouchTap={actionCreators.closeDialog}
    />,
    <FlatButton
      label="Send Now"
      secondary
      keyboardFocused
      onTouchTap={() =>
        actionCreators.confirmSendBroadcast(props.payload)}
    />,
  ]

  return (
    <Dialog
      actions={actions}
      title="Confirm Send"
      open={props.open}
      onRequestClose={actionCreators.closeDialog}
    >
      { 'Are you sure to send this broadcast message?' }
    </Dialog>
  )
}

BroadcastSendDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.shape({}).isRequired,
}

const ConnectedBroadcastSendDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(BroadcastSendDialog)

export default ConnectedBroadcastSendDialog
