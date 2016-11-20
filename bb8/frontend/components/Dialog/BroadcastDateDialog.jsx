import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'

import * as dialogActionCreators from '../../actions/dialogActionCreators'

class BroadcastDateDialog extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      date: new Date(),
    }
  }

  render() {
    const actionCreators = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={actionCreators.closeDialog}
      />,
      <FlatButton
        label="Save"
        secondary
        keyboardFocused
        onTouchTap={() =>
          actionCreators.confirmBroadcastDate(
            this.props.payload, this.state.date)}
      />,
    ]

    return (
      <Dialog
        actions={actions}
        title="Please choose a date"
        open={this.props.open}
        onRequestClose={actionCreators.closeDialog}
      >
        { 'some date picker here...' }
      </Dialog>
    )
  }
}

BroadcastDateDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.shape({}).isRequired,
}

const ConnectedBroadcastDateDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(BroadcastDateDialog)

export default ConnectedBroadcastDateDialog
