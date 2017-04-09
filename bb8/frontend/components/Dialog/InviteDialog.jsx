import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import validator from 'validator'
import Subheader from 'material-ui/Subheader'
import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'

import * as accountActionCreators from '../../actions/accountActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'
import * as uiActionCreators from '../../actions/uiActionCreators'

const INVITE_CODE = 'invite-code'

const styles = {
  textField: {
    width: '80%',
  },
}

class InviteDialog extends React.Component {
  constructor(props) {
    super(props)

    this.copyText = this.copyText.bind(this)
    this.handleEmailChange = this.handleEmailChange.bind(this)

    this.accountActions = bindActionCreators(
      accountActionCreators, this.props.dispatch)
    this.dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)
    this.uiActions = bindActionCreators(
      uiActionCreators, this.props.dispatch)

    this.state = {
      email: '',
      emailError: '',
    }
  }

  copyText() {
    const copyTextArea = document.querySelector(`#${INVITE_CODE}`)
    copyTextArea.select()

    const successful = document.execCommand('copy')
    const message = successful ?
      'The invitation code is copied to clipboard' :
      'Sorry, unable to copy to clipboard'

    this.uiActions.openNotification(message)
  }

  handleEmailChange(e, email) {
    if (validator.isEmail(email)) {
      this.setState({
        email,
        emailError: '',
      })
    } else {
      this.setState({
        email,
        emailError: 'Please provide a valid email address',
      })
    }
  }

  render() {
    const actions = [
      <FlatButton
        label="Invite"
        primary
        disabled={!validator.isEmail(this.state.email)}
        onTouchTap={() => this.accountActions.invite(this.state.email)}
      />,
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.dialogActions.closeDialog}
      />,
    ]
    return (
      <Dialog
        title={'Invite User'}
        actions={actions}
        open={this.props.open}
        onRequestClose={this.dialogActions.closeDialog}
      >
        <div>
          <Subheader>
            Who would you like to invite?
          </Subheader>
          <TextField
            style={styles.textField}
            hintText="Please enter the email to invite him"
            errorText={this.state.emailError}
            value={this.state.email}
            onChange={this.handleEmailChange}
          />
        </div>
        <div
          style={{ display: this.props.inviteCode ? 'inherit' : 'none' }}
        >
          <Subheader>
            Here is your invitation code
          </Subheader>
          <TextField
            style={styles.textField}
            multiLine
            id={INVITE_CODE}
            hintText="Invitation code"
            value={this.props.inviteCode}
            onClick={this.copyText}
          />
        </div>
      </Dialog>
    )
  }
}

InviteDialog.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  inviteCode: React.PropTypes.string,
  open: React.PropTypes.bool.isRequired,
  payload: React.PropTypes.shape({}),
}

const ConnectedInviteDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
    inviteCode: state.account.inviteCode,
  }),
)(InviteDialog)

export default ConnectedInviteDialog
