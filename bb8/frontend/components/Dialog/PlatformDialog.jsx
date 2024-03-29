import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import uuid from 'node-uuid'

import Avatar from 'material-ui/Avatar'
import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import TextField from 'material-ui/TextField'
import Paper from 'material-ui/Paper'
import Popover from 'material-ui/Popover'
import Divider from 'material-ui/Divider'
import Subheader from 'material-ui/Subheader'
import { Menu, MenuItem } from 'material-ui/Menu'
import { List, ListItem } from 'material-ui/List'
import IconArrowDropDown from 'material-ui/svg-icons/navigation/arrow-drop-down'

import config from '../../config'
import * as platformActionCreators from '../../actions/platformActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'
import * as miscActionCreators from '../../actions/miscActionCreators'

import FbMessengerIcon from '../../assets/svgIcon/FbMessengerIcon'
import LineIcon from '../../assets/svgIcon/LineIcon'

const styles = {
  titleStyle: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  bodyStyle: {
    overflowY: 'scroll',
  },
  rows: {
    display: 'flex',
    alignItems: 'center',
    paddingRight: '10%',
  },
  hintStyle: {
    color: '#bbb',
  },
  typePickerContainer: {
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
  },
  emptyState: {
    textAlign: 'center',
    margin: '1.5em 0',
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

  componentDidMount() {
    this.props.dispatch(miscActionCreators.refreshFacebookPages())
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

  handleTypeEnumChange(typeEnum) {
    if (typeEnum === 'Line') {
      this.setState({
        platform: {
          ...this.props.payload,
          typeEnum,
          providerIdent: uuid.v4(),
        },
        platformTypePickerOpen: false,
      })
    } else {
      this.setState({
        platform: {
          ...this.state.platform,
          typeEnum,
          providerIdent: '',
        },
        platformTypePickerOpen: false,
      })
    }
  }

  handlePageChange(idx) {
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

    const LineAvatar = (<Avatar
      backgroundColor="#00B900"
      color="white"
    >
      <LineIcon style={{ color: 'white' }} />
    </Avatar>)

    const FbAvatar = (<Avatar
      backgroundColor="#0084FF"
      color="white"
    >
      <FbMessengerIcon style={{ color: 'white' }} />
    </Avatar>)

    const platformTypePicker = (<div
      onMouseEnter={() => this.setState({ platformTypePickerHover: true })}
      onMouseLeave={() => this.setState({ platformTypePickerHover: false })}
      onClick={(e) => {
        this.setState({
          platformTypePickerOpen: true,
          platformTypePickerEl: e.currentTarget,
        })
      }}
      style={styles.typePickerContainer}
    >
      <Paper
        circle
        zDepth={this.state.platformTypePickerHover || this.state.platformTypePickerOpen ? 0 : 1}
        style={{
          display: 'flex',
          opacity: this.state.platformTypePickerHover ||
                   this.state.platformTypePickerOpen ? 0.5 : 1,
        }}
      >
        {platform.typeEnum === 'Line' ? LineAvatar : FbAvatar}
      </Paper>
      { !isUpdating && (
        <div>
          <IconArrowDropDown />
          <Popover
            open={this.state.platformTypePickerOpen}
            anchorEl={this.state.platformTypePickerEl}
            anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
            targetOrigin={{ horizontal: 'right', vertical: 'top' }}
            onRequestClose={() => this.setState({
              platformTypePickerOpen: false,
              platformTypePickerHover: false,
            })}
          >
            <Menu style={{ minWidth: '10em' }}>
              <MenuItem primaryText="Facebook" onClick={() => this.handleTypeEnumChange('Facebook')} />
              <MenuItem primaryText="Line" onClick={() => this.handleTypeEnumChange('Line')} />
            </Menu>
          </Popover>
        </div>)
      }
    </div>)

    const facebookForm = Object.values(this.props.pages).length > 0 ? (
      <List>
        <Subheader>Choose from existing facebook page:</Subheader>
        {
          Object.keys(this.props.pages).map((idx) => {
            const page = this.props.pages[idx]
            const { selectedId } = this.state
            const { available } = page

            return [
              idx > 0 && <Divider />,
              <ListItem
                key={idx}
                value={idx}
                primaryText={page.name}
                secondaryText={page.about}
                leftAvatar={<Avatar src={page.picture.data.url} />}
                onClick={() => available && this.handlePageChange(idx)}
                innerDivStyle={{
                  ...(selectedId && selectedId !== idx) || !available ? { opacity: 0.3 } : {},
                }}
                disabled={!available}
              />,
            ]
          })
        }
      </List>
    ) : (<Subheader style={styles.emptyState}>
      {'You don\'t have any page.'}
    </Subheader>)

    const lineForm = [
      <div style={styles.rows}>
        <TextField
          floatingLabelText="Channel Name"
          value={platform.name}
          onChange={this.handleNameChange}
          fullWidth
        />
        <TextField
          floatingLabelText="Channel Secret"
          value={platform.config.channelSecret}
          onChange={this.handleChannelSecretChange}
          fullWidth
        />
      </div>,
      <div style={styles.rows}>
        <TextField
          floatingLabelText="Channel Access Token"
          value={platform.config.accessToken}
          onChange={this.handleAccessTokenChange}
          onFocus={(e) => { e.target.select() }}
          multiLine
          fullWidth
        />
      </div>,
      <div style={styles.rows}>
        <TextField
          floatingLabelText="Webhook Url"
          value={`${config.LINE_WEBHOOK}${platform.providerIdent}`}
          fullWidth
          onFocus={(e) => { e.target.select() }}
          errorText="Paste this webhook url to LINE@ channel settings"
          errorStyle={styles.hintStyle}
        />
      </div>,
    ]

    const title = (<div style={styles.titleStyle}>
      {[
        isUpdating ?
          <span> Edit
            <b style={{ textTransform: 'capitalize' }}>
              {platform.name}
            </b>
          </span> : 'New Platform',
        platformTypePicker,
      ]}
    </div>)

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
        title={title}
        actions={actions}
        open={this.props.open}
        onRequestClose={this.dialogActions.closeDialog}
        bodyStyle={styles.bodyStyle}
      >
        {[
          platform.typeEnum === 'Facebook' && facebookForm,
          platform.typeEnum === 'Line' && lineForm,
        ]}
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
  (state) => {
    const providerIdents = state.platforms.ids.map(
      idx => state.entities.platforms[idx].providerIdent)

    return {
      pages: state.entities.fbpages ? Object.keys(state.entities.fbpages).map(idx => ({
        available: providerIdents.indexOf(state.entities.fbpages[idx].pageId) === -1,
        ...state.entities.fbpages[idx],
      })) : [],
      open: state.dialog.open,
      payload: state.dialog.payload,
    }
  }
)(PlatformDialog)

export default ConnectedPlatformDialog
