import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'

import * as dialogActionCreators from '../../actions/dialogActionCreators'

class BroadcastDateDialog extends React.Component {
  constructor(props) {
    super(props)

    this.handleDateChange = this.handleDateChange.bind(this)
    this.handleTimeChange = this.handleTimeChange.bind(this)
    this.state = {
      date: new Date(),
    }
  }

  // FIXME(kevin): temporarily disable lint until this is implemented
  // eslint-disable-next-line class-methods-use-this
  handleDateChange() {

  }

  // FIXME(kevin): temporarily disable lint until this is implemented
  // eslint-disable-next-line class-methods-use-this
  handleTimeChange() {

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
        <TextField
          hintText="mm/dd/yyyy"
          onChange={this.handleDateChange}
        />
        <TextField
          hintText="hh/mm"
          onChange={this.handleTimeChange}
        />
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
