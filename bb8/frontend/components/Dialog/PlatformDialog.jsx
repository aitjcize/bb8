import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import uuid from 'node-uuid'

import DropDownMenu from 'material-ui/DropDownMenu'
import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'
import SelectField from 'material-ui/SelectField'
import MenuItem from 'material-ui/MenuItem'

import config from '../../config'
import * as platformActionCreators from '../../actions/platformActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'

const styles = {
  dropdownStyle: {
    width: '10em',
  },
  listStyle: {
    width: '30em',
  },
}

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
    this.handlePageChange = this.handlePageChange.bind(this)

    this.state = {
      platform: { ...props.payload, typeEnum: props.payload.typeEnum || 'Facebook' },
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

  handlePageChange(e, key, idx) {
    this.setState({ selectedId: idx })
    const page = this.props.pages[idx]

    this.setState({
      platform: {
        ...this.state.platform,
        typeEnum: 'Facebook',
        name: page.name,
        providerIdent: page.pageId,
        config: { accessToken: page.accessToken },
      },
    })
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

    const fbPagePicker = (
      <DropDownMenu
        listStyle={styles.listStyle}
        value={this.state.selectedId}
        onChange={this.handlePageChange}
      >
        {
          Object.keys(this.props.pages).map((idx) => {
            const page = this.props.pages[idx]

            return (<MenuItem
              key={idx}
              value={idx}
              primaryText={page.name}
              secondaryText={page.about.length < 15 ? page.about : `${page.about.substring(0, 15)}...`}
              leftIcon={<img alt="page" src={page.picture.data.url} />}
            />)
          })
        }
      </DropDownMenu>)

    return (
      <Dialog
        title={isUpdating ? 'Edit Platform' : 'New Platform'}
        actions={actions}
        open={this.props.open}
        onRequestClose={this.dialogActions.closeDialog}
      >
        <SelectField
          floatingLabelText="Platform Type"
          value={platform.typeEnum}
          onChange={this.handleTypeEnumChange}
        >
          <MenuItem value={'Facebook'} primaryText="Facebook" />
          <MenuItem value={'Line'} primaryText="Line" />
        </SelectField>

        {
          platform.typeEnum === 'Facebook' ? fbPagePicker :
          <div>
            <TextField
              floatingLabelText="Platform Name"
              hintText="Platform Name"
              value={platform.name}
              onChange={this.handleNameChange}
            />
            <div>
              Webhook: { config.LINE_WEBHOOK + platform.providerIdent }
            </div> :
            <TextField
              floatingLabelText="Page ID"
              hintText="Page ID"
              value={platform.providerIdent}
              onChange={this.handleProviderIdentChange}
            />
            <TextField
              hintText="Access Token"
              floatingLabelText="Access Token"
              value={platform.config.accessToken}
              onChange={this.handleAccessTokenChange}
            />
            <TextField
              floatingLabelText="Channel Secret"
              hintText="Channel Secret"
              value={platform.config.channelSecret}
              onChange={this.handleChannelSecretChange}
            />
          </div>
        }
      </Dialog>
    )
  }
}

PlatformDialog.propTypes = {
  open: React.PropTypes.bool.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  payload: React.PropTypes.shape({
    typeEnum: React.PropTypes.string,
    config: React.PropTypes.shape({}),
  }),
  pages: React.PropTypes.shape({}),
}

PlatformDialog.defaultProps = {
  payload: {
    config: {},
  },
}

const ConnectedPlatformDialog = connect(
  state => ({
    pages: state.entities.fbpages,
    open: state.dialog.open,
    payload: state.dialog.payload,
  }),
)(PlatformDialog)

export default ConnectedPlatformDialog
