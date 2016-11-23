import React from 'react'
import { connect } from 'react-redux'
import TextField from 'material-ui/TextField'
import RaisedButton from 'material-ui/RaisedButton'
import uuid from 'node-uuid'

import SelectField from 'material-ui/SelectField'
import MenuItem from 'material-ui/MenuItem'

import config from '../../config'
import { createPlatform, updatePlatform } from '../../actions/platformActionCreators'
import { openNotification } from '../../actions/uiActionCreators'


class PlatformForm extends React.Component {
  constructor(props) {
    super(props)

    this.onNameChange = this.onNameChange.bind(this)
    this.onTypeEnumChange = this.onTypeEnumChange.bind(this)
    this.onAccessTokenChange = this.onAccessTokenChange.bind(this)
    this.onChannelSecretChange = this.onChannelSecretChange.bind(this)
    this.onProviderIdentChange = this.onProviderIdentChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)

    this.state = {
      id: props.platform.id,
      name: props.platform.name,
      typeEnum: props.platform.typeEnum || 'Facebook',
      providerIdent: props.platform.providerIdent,
      accessToken: props.platform.config.accessToken,
      channelSecret: props.platform.config.channelSecret,
    }
  }

  onTypeEnumChange(e, idx, typeEnum) {
    if (typeEnum === 'Line') {
      this.setState({ typeEnum, providerIdent: uuid.v4() })
    } else {
      this.setState({ typeEnum, providerIdent: '' })
    }
  }

  onNameChange(e, name) {
    this.setState({ name })
  }

  onProviderIdentChange(e, providerIdent) {
    this.setState({ providerIdent })
  }

  onAccessTokenChange(e, accessToken) {
    this.setState({ accessToken })
  }

  onChannelSecretChange(e, channelSecret) {
    this.setState({ channelSecret })
  }

  handleSubmit(e) {
    e.preventDefault()

    if (!this.state.name) {
      this.props.handleShowNotification('Please provide a name for this platform')
      return
    } else if (!this.state.providerIdent) {
      this.props.handleShowNotification('Please provide the platform id of this platform')
      return
    } else if (!this.state.accessToken) {
      this.props.handleShowNotification('Please provide the access token of this platform')
      return
    }

    this.props.handleClose()

    const platform = {
      name: this.state.name,
      typeEnum: this.state.typeEnum,
      providerIdent: this.state.providerIdent,
      deployed: true,
      config: {
        accessToken: this.state.accessToken,
      },
    }
    if (this.state.typeEnum === 'Line') {
      platform.config.channelSecret = this.state.channelSecret
    }

    if (!this.state.id) {
      this.props.handleCreatePlatform(platform)
    } else {
      this.props.handleUpdatePlatform(this.state.id, platform)
    }
  }

  render() {
    return (
      <form>
        <TextField
          hintText="Platform Name"
          value={this.state.name}
          onChange={this.onNameChange}
        />

        <SelectField
          floatingLabelText="Platform Type"
          value={this.state.typeEnum}
          onChange={this.onTypeEnumChange}
        >
          <MenuItem value={'Facebook'} primaryText="Facebook" />
          <MenuItem value={'Line'} primaryText="Line" />
        </SelectField>

        { this.state.typeEnum === 'Line' ?
          <div>
            Webhook: { config.LINE_WEBHOOK + this.state.providerIdent }
          </div> :
          <TextField
            hintText="Page ID"
            value={this.state.providerIdent}
            onChange={this.onProviderIdentChange}
          />
        }

        <TextField
          hintText="Access Token"
          value={this.state.accessToken}
          onChange={this.onAccessTokenChange}
        />

        {
          this.state.typeEnum === 'Facebook' ? null :
          <TextField
            hintText="Channel Secret"
            value={this.state.channelSecret}
            onChange={this.onChannelSecretChange}
          />
        }

        <RaisedButton
          onClick={this.handleSubmit}
          className="b-platform-form__button"
          type="submit"
          label={!this.state.id ? 'Create' : 'Save'}
          primary
        />
      </form>)
  }
}

PlatformForm.propTypes = {
  handleClose: React.PropTypes.func,
  handleUpdatePlatform: React.PropTypes.func,
  handleCreatePlatform: React.PropTypes.func,
  handleShowNotification: React.PropTypes.func,
  platform: React.PropTypes.shape({
    id: React.PropTypes.number,
    name: React.PropTypes.string,
    typeEnum: React.PropTypes.string,
    providerIdent: React.PropTypes.string,
    config: React.PropTypes.shape({
      accessToken: React.PropTypes.string,
      channelSecret: React.PropTypes.string,
    }),
  }),
}

const ConnectedPlatformForm = connect(
  () => ({}),
  dispatch => ({
    handleUpdatePlatform(platformId, platform) {
      dispatch(updatePlatform(platformId, platform))
    },
    handleCreatePlatform(platform) {
      dispatch(createPlatform(platform))
    },
    handleShowNotification(message) {
      dispatch(openNotification(message))
    },
  }),
)(PlatformForm)

export default ConnectedPlatformForm
