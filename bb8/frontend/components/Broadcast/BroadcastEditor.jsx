import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import stylePropType from 'react-style-proptype'

import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'
import { Card, CardActions, CardHeader } from 'material-ui/Card'

import Message from '../modules/Message'
import * as uiActionCreators from '../../actions/uiActionCreators'
import * as broadcastActionCreators from '../../actions/broadcastActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'

class BroadcastEditor extends React.Component {
  constructor(props) {
    super(props)

    this.handleNameChange = this.handleNameChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)

    this.broadcastActions = bindActionCreators(
      broadcastActionCreators, this.props.dispatch)
    this.uiActions = bindActionCreators(
      uiActionCreators, this.props.dispatch)

    this.state = {
      nameError: '',
      scheduling: false,
      datepickerVal: null,
      timepickerVal: null,
      broadcast: props.broadcast,
    }
  }

  componentDidMount() {
    if (this.props.broadcast && this.props.broadcast.messages) {
      this.editor.clear()
      this.editor.fromJSON(this.props.broadcast)
    }
  }

  getBroadcast() {
    const messages = this.editor.toJSON()
    const err = new Error()
    if (!this.state.broadcast.name) {
      err.errorMessage = 'Please provide a name for this broadcast'
      throw err
    } else if (this.state.broadcast.name.length > 30) {
      err.errorMessage = 'The name of the broadcast is too long'
      throw err
    } else if (this.state.scheduling &&
        (!this.state.timepickerVal ||
         !this.state.datepickerVal)) {
      err.errorMessage = 'Please pick a date and a time'
      throw err
    } else if (!messages.messages || messages.messages.length === 0) {
      err.errorMessage = 'Cannot save a broadcast with no message'
      throw err
    }

    const broadcast = {
      ...this.state.broadcast,
      botId: this.props.activeBotId,
      messages: messages.messages,
    }

    if (!broadcast.scheduledTime) {
      broadcast.scheduledTime = 0
    }
    return broadcast
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
    this.props.handleCloseEditor()

    let broadcast
    try {
      broadcast = this.getBroadcast()
    } catch (e) {
      this.uiActions.openNotification(e.errorMessage)
    }

    if (!broadcast.id) {
      this.broadcastActions.createBroadcast(broadcast)
    } else {
      this.broadcastActions.updateBroadcast(
        broadcast.id, broadcast)
    }
    this.uiActions.openNotification('Successfully saved the broadcast')
  }

  render() {
    const styles = this.props.styles

    const dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    const isSent = (this.props.broadcast.status === 'Sent' ||
                    this.props.broadcast.status === 'Sending')

    return (
      <Card>
        <CardHeader
          title={
            <TextField
              disabled={isSent}
              hintText="give this broadcast a name"
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
          readOnly={isSent}
          maxMessages={5}
          ref={(m) => {
            this.editor = m
          }}
        />
        <CardActions style={styles.infoActionsContainer}>
          <div style={styles.infoActionsGroup}>
            {
             !isSent &&
             <FlatButton
               onClick={() => this.handleSubmit(this.props.broadcast)}
               label="Save"
             />
            }
            <FlatButton
              onClick={this.props.handleCloseEditor}
              label="Cancel"
              secondary
            />
          </div>
          <div style={{ ...styles.infoActionsGroup, ...{ flex: 'none' } }}>
            {
              !isSent &&
              <FlatButton
                onClick={() => {
                  try {
                    const broadcast = this.getBroadcast()
                    dialogActions.openSendBroadcast(broadcast)
                  } catch (e) {
                    this.uiActions.openNotification(e.errorMessage)
                  }
                }}
                label="send now"
                primary
              />
            }
          </div>
        </CardActions>
      </Card>
    )
  }
}

BroadcastEditor.propTypes = {
  dispatch: React.PropTypes.func,
  activeBotId: React.PropTypes.number,
  styles: React.PropTypes.objectOf(stylePropType),
  broadcast: React.PropTypes.shape({
    status: React.PropTypes.string,
    messages: React.PropTypes.arrayOf(React.PropTypes.shape({})),
  }),
  handleCloseEditor: React.PropTypes.func,
}

const ConnectedBroadcastEditor = connect(
  state => ({
    activeBotId: state.bots.active,
  }),
)(BroadcastEditor)

export default ConnectedBroadcastEditor
