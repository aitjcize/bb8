import Moment from 'moment'
import React from 'react'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import DatePicker from 'material-ui/DatePicker'
import TimePicker from 'material-ui/TimePicker'
import TextField from 'material-ui/TextField'
import RaisedButton from 'material-ui/RaisedButton'

import Message from '../content_modules/Message'
import { createBroadcast, updateBroadcast, openNotification } from '../../actions'


function combineDateTime(date, time) {
  if (!date || !time) {
    return null
  }

  const d = Moment(date)
  const t = Moment(time)

  const scheduledTime = Moment(d)
  scheduledTime
    .hours(t.hours())
    .minutes(t.minutes())
    .seconds(t.seconds())
  return scheduledTime.unix()
}

class BroadcastEditor extends React.Component {
  constructor(props) {
    super(props)

    this.handleNameChange = this.handleNameChange.bind(this)
    this.handleDateChange = this.handleDateChange.bind(this)
    this.handleTimeChange = this.handleTimeChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)

    this.state = {
      nameError: '',
      scheduling: false,
      datepickerVal: null,
      timepickerVal: null,
      broadcast: props.broadcast,
      dialogOpen: false,
    }
  }

  componentWillReceiveProps(nextProps) {
    this.setState({
      nameError: '',
      broadcast: nextProps.broadcast,
    })
    this.editor.clear()
    if (nextProps.broadcast && nextProps.messages) {
      this.editor.fromJSON(nextProps.broadcast)
    }
  }

  handleNameChange(e) {
    const name = e.target.value
    if (!name) {
      this.setState({
        nameError: 'Please give this broadcast a name',
        broadcast: Object.assign({}, this.state.broadcast, { name }),
      })
    } else if (name.length > 30) {
      this.setState({
        nameError: 'The length of name should be smaller than 30',
        broadcast: Object.assign({}, this.state.broadcast, { name }),
      })
    } else {
      this.setState({
        nameError: '',
        broadcast: Object.assign({}, this.state.broadcast, { name }),
      })
    }
  }

  handleDateChange(e, date) {
    const scheduledTime = combineDateTime(
      date, this.state.timepickerVal)

    this.setState({
      datepickerVal: date,
      broadcast: Object.assign(
        {}, this.state.broadcast, { scheduledTime }
      ),
    })
  }

  handleTimeChange(e, time) {
    const scheduledTime = combineDateTime(
      this.state.datepickerVal, time)

    this.setState({
      timepickerVal: time,
      broadcast: Object.assign(
        {}, this.state.broadcast, { scheduledTime }
      ),
    })
  }

  handleSubmit() {
    this.setState({ dialogOpen: false })

    if (!this.state.broadcast.name) {
      this.props.handleShowNotification('Please provide a name for this broadcast')
      return
    } else if (this.state.broadcast.name.length > 30) {
      this.props.handleShowNotification('The name of the broadcast is too long')
      return
    } else if (this.state.scheduling &&
        (!this.state.timepickerVal ||
         !this.state.datepickerVal)) {
      this.props.handleShowNotification('Please pick a date and a time')
      return
    }

    this.props.handleCloseEditor()
    const messages = this.editor.toJSON()
    const broadcast = {
      name: this.state.broadcast.name,
      scheduledTime: this.state.broadcast.scheduledTime,
      botId: this.props.activeBotId,
      messages: messages.messages,
    }

    if (!broadcast.scheduledTime) {
      broadcast.scheduledTime = 0
    }

    if (!this.state.broadcast.id) {
      this.props.handleCreateBroadcast(broadcast)
    } else {
      this.props.handleUpdateBroadcast(
        this.state.broadcast.id, broadcast)
    }
  }

  render() {
    const sendActions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={() => this.setState({ dialogOpen: false })}
      />,
      <FlatButton
        label="Yes"
        secondary
        keyboardFocused
        onTouchTap={this.handleSubmit}
      />,
    ]
    return (
      <div>
        <Dialog
          title="Confirm Send"
          actions={sendActions}
          modal={false}
          open={this.state.dialogOpen}
          onRequestClose={() => this.setState({ dialogOpen: false })}
        >
          { 'Are you sure to send this broadcast message?' }
        </Dialog>
        <TextField
          value={this.state.broadcast.name || ''}
          hintText="Give this broadcast a name"
          errorText={this.state.nameError}
          onChange={this.handleNameChange}
        />
        <Message
          editorWidth="300px"
          maxMessages={5}
          ref={(m) => {
            this.editor = m
          }}
        />
        { !this.state.scheduling ? null :
          <div>
            <DatePicker
              autoOk
              hintText="Tell me a date"
              container="inline"
              value={this.state.datepickerVal}
              onChange={this.handleDateChange}
            />
            <TimePicker
              autoOk
              hintText="Tell me a time"
              value={this.state.timepickerVal}
              onChange={this.handleTimeChange}
            />
          </div>
        }
        <RaisedButton
          label="Send Now"
          primary
          onClick={() => this.setState({ dialogOpen: true })}
        />

        { this.state.scheduling ?
          <RaisedButton
            label="Save"
            onClick={this.handleSubmit}
          /> :
            <RaisedButton
              label="Schedule"
              onClick={() => this.setState(prevState => ({
                ...prevState,
                scheduling: true,
              }))}
            />
        }
      </div>
    )
  }
}

BroadcastEditor.propTypes = {
  activeBotId: React.PropTypes.number,
  broadcast: React.PropTypes.shape({}),
  handleUpdateBroadcast: React.PropTypes.func,
  handleCreateBroadcast: React.PropTypes.func,
  handleCloseEditor: React.PropTypes.func,
  handleShowNotification: React.PropTypes.func,
}

const ConnectedBroadcastEditor = connect(
  state => ({
    activeBotId: state.bots.active,
  }),
  dispatch => ({
    handleUpdateBroadcast(broadcastId, broadcast) {
      dispatch(updateBroadcast(broadcastId, broadcast))
    },
    handleCreateBroadcast(broadcast) {
      dispatch(createBroadcast(broadcast))
    },
    handleShowNotification(message) {
      dispatch(openNotification(message))
    },
  }),
)(BroadcastEditor)

export default ConnectedBroadcastEditor
