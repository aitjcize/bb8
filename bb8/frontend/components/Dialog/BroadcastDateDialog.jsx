import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import VMasker from 'vanilla-masker'
import Moment from 'moment'

import DatePicker from 'material-ui/DatePicker'
import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'

import * as dialogActionCreators from '../../actions/dialogActionCreators'
import * as uiActionCreators from '../../actions/uiActionCreators'

const leftPad = (integer, totalSize) =>
  `${'0'.repeat(totalSize - integer.toString().length)}${integer}`

class BroadcastDateDialog extends React.Component {
  constructor(props) {
    super(props)

    this.handleDateChange = this.handleDateChange.bind(this)
    this.handleTimeChange = this.handleTimeChange.bind(this)

    const d = this.props.payload.scheduledTime

    if (!d) {
      this.state = {
        dateVal: '',
        dateError: '',
        timeVal: '',
        timeError: '',
      }
    } else {
      const date = new Date(d * 1000)
      this.state = {
        dateVal: Moment(date).format('YYYY-MM-DD'),
        timeVal: `${leftPad(date.getHours(), 2)}:${leftPad(date.getMinutes(), 2)}`,
      }
    }
  }

  get date() {
    const dateArray = Moment(this.state.dateVal).format('YYYY-MM-DD')
                          .split('-')
                          .map(elem => parseInt(elem, 10))
    const timeArray = this.state.timeVal.split(':')
                          .map(elem => parseInt(elem, 10))

    const d = new Date()
    d.setFullYear(dateArray[0], dateArray[1] - 1, dateArray[2])
    d.setHours(...timeArray)

    return d
  }

  handleDateChange(e, date) {
    this.setState({ dateVal: Moment(date).format('MM-DD-YYYY') })
  }

  handleTimeChange(e) {
    const mask = '99:99'
    const maskValue = VMasker.toPattern(e.target.value, mask)
    const values = maskValue.split(':').map(elem => parseInt(elem, 10))
    if (values.length !== 2) {
      this.setState({ timeVal: maskValue, timeError: 'please provide the time in hh:mm format' })
    } else if (values[0] === '' || values[0] < 0 || values[0] > 24) {
      this.setState({ timeVal: maskValue, timeError: 'the hour should be between 0 and 24' })
    } else if (values[1] === '' || values[1] < 0 || values[1] > 60) {
      this.setState({ timeVal: maskValue, timeError: 'the minute should be between 0 and 60' })
    } else {
      this.setState({ timeVal: maskValue, timeError: '' })
    }
  }

  render() {
    const actionCreators = bindActionCreators(
      dialogActionCreators, this.props.dispatch)
    const uiActions = bindActionCreators(
      uiActionCreators, this.props.dispatch)

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
        onTouchTap={() => {
          if (this.state.timeError) {
            uiActions.openNotification('Please pick a correct date and time')
          } else {
            actionCreators.confirmBroadcastDate(
              this.props.payload, this.date)
          }
        }}
      />,
    ]

    const minDate = new Date()
    minDate.setHours(0, 0, 0, 0)

    return (
      <Dialog
        actions={actions}
        title="Please choose a date"
        open={this.props.open}
        onRequestClose={actionCreators.closeDialog}
      >
        <DatePicker
          hintText="yyyy-mm-dd"
          minDate={minDate}
          autoOk
          value={Moment(this.state.dateVal).toDate()}
          onChange={this.handleDateChange}
        />

        <TextField
          hintText="hh:mm"
          errorText={this.state.timeError}
          value={this.state.timeVal}
          onChange={this.handleTimeChange}
        />
      </Dialog>
    )
  }
}

BroadcastDateDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.shape({
    scheduledTime: React.PropTypes.number.isRequired,
  }).isRequired,
}

const ConnectedBroadcastDateDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(BroadcastDateDialog)

export default ConnectedBroadcastDateDialog
