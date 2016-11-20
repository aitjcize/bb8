import React from 'react'
import { connect } from 'react-redux'

import stylePropType from 'react-style-proptype'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'
import { Card, CardActions, CardHeader } from 'material-ui/Card'

import Message from '../modules/Message'
import { createBroadcast, updateBroadcast } from '../../actions/broadcastActionCreators'
import { openNotification } from '../../actions/uiActionCreators'

class BroadcastEditor extends React.Component {
  constructor(props) {
    super(props)

    this.handleNameChange = this.handleNameChange.bind(this)
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

  componentDidMount() {
    if (this.props.broadcast && this.props.broadcast.messages) {
      this.editor.clear()
      this.editor.fromJSON(this.props.broadcast)
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

  handleSubmit() {
    this.setState({ dialogOpen: false })

    const messages = this.editor.toJSON()
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
    } else if (!messages.messages || messages.messages.length === 0) {
      this.props.handleShowNotification('Cannot save a broadcast with no message')
      return
    }

    this.props.handleShowNotification('Successfully saved the broadcast')

    this.props.handleCloseEditor()
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
    const styles = this.props.styles

    return (
      <Card>
        <Dialog
          title="Confirm Send"
          actions={sendActions}
          modal={false}
          open={this.state.dialogOpen}
          onRequestClose={() => this.setState({ dialogOpen: false })}
        >
          { 'Are you sure to send this broadcast message?' }
        </Dialog>
        <CardHeader
          title={
            <TextField
              errorText={this.state.nameError}
              onChange={this.handleNameChange}
              value={this.state.broadcast.name}
              style={{
                minWidth: '25vw',
              }}
            />
          }
          titleStyle={{
            paddingLeft: '1em',
          }}
          subtitle={this.state.broadcast.status}
          subtitleStyle={{
            paddingLeft: '1em',
          }}
        />
        <Message
          maxMessages={5}
          ref={(m) => {
            this.editor = m
          }}
        />
        <CardActions style={styles.infoActionsContainer}>
          <div style={styles.infoActionsGroup}>
            <FlatButton
              onClick={() => this.handleSubmit(this.props.broadcast)}
              label="Save"
            />
            <FlatButton
              onClick={this.props.handleCloseEditor}
              label="Cancel"
              secondary
            />
          </div>
          <div style={{ ...styles.infoActionsGroup, ...{ flex: 'none' } }}>
            <FlatButton
              onClick={() => this.setState({ dialogOpen: true })}
              label="Send Now"
              primary
            />
          </div>
        </CardActions>
      </Card>
    )
  }
}

BroadcastEditor.propTypes = {
  activeBotId: React.PropTypes.number,
  styles: React.PropTypes.objectOf(stylePropType),
  broadcast: React.PropTypes.shape({
    messages: React.PropTypes.arrayOf(React.PropTypes.shape({})),
  }),
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
