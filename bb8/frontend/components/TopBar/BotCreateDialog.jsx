import React from 'react'
import { connect } from 'react-redux'
import Subheader from 'material-ui/Subheader'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'

import { createBot } from '../../actions'

const NAME_LIMIT = 30
const DESC_LIMIT = 150

class BotCreateDialog extends React.Component {
  constructor(props) {
    super(props)

    this.handleCreateBot = this.handleCreateBot.bind(this)
    this.handleNameChange = this.handleNameChange.bind(this)
    this.handleDescChange = this.handleDescChange.bind(this)

    this.state = {
      name: '',
      nameError: '',
      description: '',
      descriptionError: '',
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
    this.props.dispatchCreateBot(bot)
    this.props.handleClose()
    this.setState({
      name: '',
      description: '',
    })
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

  render() {
    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.props.handleClose}
      />,
      <FlatButton
        label="Create"
        primary
        onTouchTap={this.handleCreateBot}
      />,
    ]

    return (
      <Dialog
        title="New Chatbot"
        actions={actions}
        open={this.props.open}
        modal
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
      </Dialog>
    )
  }
}

BotCreateDialog.propTypes = {
  open: React.PropTypes.bool,
  handleClose: React.PropTypes.func,
  dispatchCreateBot: React.PropTypes.func,
}

const ConnectedBotCreateDialog = connect(
  () => ({}),
  dispatch => ({
    dispatchCreateBot(bot) {
      dispatch(createBot(bot))
    },
  }),
)(BotCreateDialog)

export default ConnectedBotCreateDialog
