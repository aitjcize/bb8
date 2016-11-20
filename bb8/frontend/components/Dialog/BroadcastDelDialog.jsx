import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'

import * as dialogActionCreators from '../../actions/dialogActionCreators'

const BroadcastDelDialog = (props) => {
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
        actionCreators.confirmDelBroadcast(props.payload)}
    />,
  ]

  return (
    <Dialog
      actions={actions}
      title="Confirm Delete"
      open={props.open}
      onRequestClose={actionCreators.closeDialog}
    >
      { 'Are you sure to delete this broadcast message?' }
    </Dialog>
  )
}

BroadcastDelDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.shape({}).isRequired,
}

const ConnectedBroadcastDelDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(BroadcastDelDialog)

export default ConnectedBroadcastDelDialog
