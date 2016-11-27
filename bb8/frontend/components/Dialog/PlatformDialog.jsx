import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import uuid from 'node-uuid'

import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'
import SelectField from 'material-ui/SelectField'
import MenuItem from 'material-ui/MenuItem'

import config from '../../config'
import * as platformActionCreators from '../../actions/platformActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'

class PlatformDialog extends React.Component {
  constructor(props) {
    super(props)

    this.dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    this.platformActions = bindActionCreators(
      platformActionCreators, this.props.dispatch)

    this.handleNameChange = this.handleNameChange.bind(this)
    this.handleProviderIdentChange = this.handleProviderIdentChange.bind(this)
    this.handleAccessTokenChange = this.handleAccessTokenChange.bind(this)
    this.handleChannelSecretChange = this.handleChannelSecretChange.bind(this)
    this.handleTypeEnumChange = this.handleTypeEnumChange.bind(this)

    this.state = {
      platform: props.payload,
    }
  }

  handleNameChange(e, name) {
    this.setState({
      platform: { ...this.state.platform, name },
    })
  }

  handleProviderIdentChange(e, providerIdent) {
    this.setState({
      platform: { ...this.state.platform, providerIdent },
    })
  }

  handleAccessTokenChange(e, accessToken) {
    this.setState({
      platform: {
        ...this.state.platform,
        config: { ...this.state.platform.config, accessToken },
      },
    })
  }

  handleChannelSecretChange(e, channelSecret) {
    this.setState({
      platform: {
        ...this.state.platform,
        config: { ...this.state.platform.config, channelSecret },
      },
    })
  }

  handleTypeEnumChange(e, idx, typeEnum) {
    if (typeEnum === 'Line') {
      this.setState({
        platform: {
          ...this.state.platform,
          typeEnum,
          providerIdent: uuid.v4(),
        },
      })
    } else {
      this.setState({
        platform: {
          ...this.state.platform,
          typeEnum,
          providerIdent: '',
        },
      })
    }
  }


  render() {
    const platform = this.state.platform
    const isUpdating = !!platform.id

    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.dialogActions.closeDialog}
      />,
      <FlatButton
        label={isUpdating ? 'Update' : 'Create'}
        primary
        onTouchTap={isUpdating ?
          () => this.dialogActions.confirmUpdatePlatform(platform) :
          () => this.dialogActions.confirmCreatePlatform(platform)
        }
      />,
    ]

    return (
      <Dialog
        title={isUpdating ? 'Edit Platform' : 'New Platform'}
        actions={actions}
        open={this.props.open}
        onRequestClose={this.dialogActions.closeDialog}
      >
        <TextField
          floatingLabelText="Platform Name"
          hintText="Platform Name"
          value={platform.name}
          onChange={this.handleNameChange}
        />
        <SelectField
          floatingLabelText="Platform Type"
          value={platform.typeEnum}
          onChange={this.handleTypeEnumChange}
        >
          <MenuItem value={'Facebook'} primaryText="Facebook" />
          <MenuItem value={'Line'} primaryText="Line" />
        </SelectField>
        {
          platform.typeEnum === 'Line' ?
            <div>
              Webhook: { config.LINE_WEBHOOK + platform.providerIdent }
            </div> :
            <TextField
              floatingLabelText="Page ID"
              hintText="Page ID"
              value={platform.providerIdent}
              onChange={this.handleProviderIdentChange}
            />
        }

        <TextField
          hintText="Access Token"
          floatingLabelText="Access Token"
          value={platform.config.accessToken}
          onChange={this.handleAccessTokenChange}
        />

        {
          platform.typeEnum === 'Line' &&
            <TextField
              floatingLabelText="Channel Secret"
              hintText="Channel Secret"
              value={platform.config.channelSecret}
              onChange={this.handleChannelSecretChange}
            />
        }
      </Dialog>
    )
  }
}

PlatformDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.shape({
    config: React.PropTypes.shape({}),
  }),
}

PlatformDialog.defaultProps = {
  payload: {
    config: {},
  },
}

const ConnectedPlatformDialog = connect(
  state => ({
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(PlatformDialog)

export default ConnectedPlatformDialog
