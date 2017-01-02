import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'

import * as dialogActionCreators from '../../actions/dialogActionCreators'

const BotDeleteDialog = (props) => {
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
        actionCreators.confirmBotDelete(props.payload)}
    />,
  ]

  return (
    <Dialog
      actions={actions}
      title="Confirm Delete"
      open={props.open}
      onRequestClose={actionCreators.closeDialog}
    >
      { 'Are you sure to delete this bot?' }
    </Dialog>
  )
}

BotDeleteDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.number.isRequired,
}

const ConnectedBotDeleteDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(BotDeleteDialog)

export default ConnectedBotDeleteDialog
