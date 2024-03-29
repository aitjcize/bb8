import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Subheader from 'material-ui/Subheader'
import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'

import * as botActionCreators from '../../actions/botActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'

const NAME_LIMIT = 30
const DESC_LIMIT = 150
const GAID_LIMIT = 50

class BotDialog extends React.Component {
  constructor(props) {
    super(props)

    this.handleCreateBot = this.handleCreateBot.bind(this)
    this.handleUpdateBot = this.handleUpdateBot.bind(this)
    this.handleNameChange = this.handleNameChange.bind(this)
    this.handleDescChange = this.handleDescChange.bind(this)
    this.handleGaIdChange = this.handleGaIdChange.bind(this)

    this.dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    this.state = {
      name: (props.payload && props.payload.name) || '',
      nameError: '',
      description: (props.payload && props.payload.description) || '',
      descriptionError: '',
      gaId: (props.payload && props.payload.gaId) || '',
      gaIdError: '',
    }
  }

  handleCreateBot() {
    if (this.state.nameError || this.state.descriptionError) {
      return
    }
    const bot = {
      name: this.state.name,
      description: this.state.description,
    }

    if (this.state.gaId && !this.state.gaIdError) {
      bot.gaId = this.state.gaId
    }

    const botActions = bindActionCreators(
      botActionCreators, this.props.dispatch)

    botActions.createBot(bot)
    this.dialogActions.closeDialog()
  }

  handleUpdateBot() {
    if (this.state.nameError || this.state.descriptionError) {
      return
    }
    const botActions = bindActionCreators(
      botActionCreators, this.props.dispatch)

    const bot = {
      name: this.state.name,
      description: this.state.description,
    }

    if (this.state.gaId && !this.state.gaIdError) {
      bot.gaId = this.state.gaId
    }

    botActions.updateBot(this.props.payload.botId, { bot })

    this.dialogActions.closeDialog()
  }

  handleNameChange(e) {
    const val = e.target.value
    if (!val) {
      this.setState({
        name: val,
        nameError: 'Please provide a name for the bot',
      })
    } else if (val.length > NAME_LIMIT) {
      this.setState({
        name: val,
        nameError: `The length of the name should be lower than ${NAME_LIMIT}`,
      })
    } else {
      this.setState({
        name: val,
        nameError: '',
      })
    }
  }

  handleDescChange(e) {
    const val = e.target.value
    if (!val) {
      this.setState({
        description: val,
        descriptionError: 'Please provide a description for the bot',
      })
    } else if (val.length > DESC_LIMIT) {
      this.setState({
        description: val,
        descriptionError: `The length of the description should be lower than ${DESC_LIMIT}`,
      })
    } else {
      this.setState({
        description: val,
        descriptionError: '',
      })
    }
  }

  handleGaIdChange(e) {
    const val = e.target.value
    if (!val) {
      this.setState({
        gaId: val,
        gaIdError: 'Please provide a Google Analytics ID for this bot',
      })
    } else if (val.length > GAID_LIMIT) {
      this.setState({
        gaId: val,
        gaIdError: `The length of the Google Analytics ID should be larger than ${GAID_LIMIT}`,
      })
    } else {
      this.setState({
        gaId: val,
        gaIdError: '',
      })
    }
  }

  render() {
    const isUpdating = !!(this.props.payload && this.props.payload.botId)
    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.dialogActions.closeDialog}
      />,
      <FlatButton
        label={isUpdating ? 'Update' : 'Create'}
        primary
        onTouchTap={isUpdating ? this.handleUpdateBot : this.handleCreateBot}
      />,
    ]

    return (
      <Dialog
        title={isUpdating ? 'Update Chatbot' : 'New Chatbot'}
        actions={actions}
        open={this.props.open}
        onRequestClose={this.dialogActions.closeDialog}
      >
        <Subheader>
          Chatbot name
        </Subheader>
        <TextField
          hintText="The name of the bot"
          errorText={this.state.nameError}
          value={this.state.name}
          onChange={this.handleNameChange}
        />
        <Subheader>
          Chatbot description
        </Subheader>
        <TextField
          hintText="The description of the bot"
          errorText={this.state.descriptionError}
          value={this.state.description}
          onChange={this.handleDescChange}
        />
        <Subheader>
          Provide a Google Analytics ID
        </Subheader>
        <TextField
          hintText="Google Analytics ID for this bot"
          errorText={this.state.gaIdError}
          value={this.state.gaId}
          onChange={this.handleGaIdChange}
        />
      </Dialog>
    )
  }
}

BotDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  payload: React.PropTypes.shape({
    botId: React.PropTypes.number.isRequired,
    name: React.PropTypes.string.isRequired,
    description: React.PropTypes.string.isRequired,
    gaId: React.PropTypes.string,
  }),
  dispatch: React.PropTypes.func.isRequired.isRequired,
}

const ConnectedBotDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(BotDialog)

export default ConnectedBotDialog
