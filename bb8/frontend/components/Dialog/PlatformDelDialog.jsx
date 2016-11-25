import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'

import * as dialogActionCreators from '../../actions/dialogActionCreators'

const PlatformDelDialog = (props) => {
  const actionCreators = bindActionCreators(
    dialogActionCreators, props.dispatch)

  const actions = [
    <FlatButton
      label="Cancel"
      primary
      onTouchTap={actionCreators.closeDialog}
    />,
    <FlatButton
      label="Delete"
      secondary
      keyboardFocused
      onTouchTap={() =>
        actionCreators.confirmDelPlatform(props.payload)}
    />,
  ]

  return (
    <Dialog
      actions={actions}
      title="Confirm Delete"
      open={props.open}
      onRequestClose={actionCreators.closeDialog}
    >
      { 'Are you sure to delete this platform?' }
    </Dialog>
  )
}

PlatformDelDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.number.isRequired,
}

const ConnectedPlatformDelDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(PlatformDelDialog)

export default ConnectedPlatformDelDialog
