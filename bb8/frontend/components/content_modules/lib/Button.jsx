import React from 'react'

import ActionSettings from 'material-ui/svg-icons/action/settings'
import ActionExitToApp from 'material-ui/svg-icons/action/exit-to-app'
import SocialShare from 'material-ui/svg-icons/social/share'
import ContentLink from 'material-ui/svg-icons/content/link'

import FloatingActionButton from 'material-ui/FloatingActionButton'
import Popover from 'material-ui/Popover'
import TextField from 'material-ui/TextField'
import { ListItem } from 'material-ui/List'
import Menu from 'material-ui/Menu'
import MenuItem from 'material-ui/MenuItem'


class Button extends React.Component {

  constructor(props) {
    super(props)

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.clearState()
    this.config_anchorEl = undefined
  }

  clearState() {
    this.state = {
      type: 'web_url',
      typeMenuOpen: false,
      typeAnchorEl: undefined,

      title: '',
      titleEditing: true,

      url: '',
      urlEditorOpen: false,
      urlEditorError: undefined,

      payload: undefined,
      payloadEditorOpen: false,
    }
  }

  valid() {
    if (!this.state.title) {
      return false
    }
    if (this.state.type === 'web_url' && !this.state.url) {
      return false
    }
    if (this.state.type === 'postback' && !this.state.payload) {
      return false
    }
    return true
  }

  validateUrl() {
    const valid = /^(http|https):\/\/[^ "]+$/.test(this.state.url)
    if (!valid && this.state.url !== '') {
      this.setState({ urlEditorError: 'Invalid URL' })
      return false
    }
    this.setState({ urlEditorError: undefined })
    return true
  }

  toJSON() {
    if (this.state.type === 'web_url') {
      return {
        type: this.state.type,
        title: this.state.title,
        url: this.state.url,
      }
    } else if (this.state.type === 'postback') {
      return {
        type: this.state.type,
        title: this.state.title,
        payload: this.state.payload,
      }
    } else if (this.state.type === 'element_share') {
      return {
        type: this.state.type,
      }
    }
    return {}
  }

  fromJSON(msg) {
    this.clearState()
    this.setState({ titleEditing: false, ...msg })
    if (msg.type === 'element_share') {
      this.setState({ title: 'Share' })
    }
  }

  render() {
    if (this.state.titleEditing) {
      return (
        <div>
          <TextField
            hintText="Button title"
            value={this.state.title}
            underlineShow={false}
            style={{ marginLeft: '16px' }}
            inputStyle={{ textAlign: 'center' }}
            hintStyle={{ left: '35%' }}
            onChange={(e) => {
              if (this.state.type !== 'element_share') {
                this.setState({ title: e.target.value })
              }
            }}
            onBlur={() => {
              if (this.state.title !== '') {
                this.setState({ titleEditing: false })
              }
            }}
            onKeyPress={(e) => {
              if (e.nativeEvent.code === 'Enter' &&
                  this.state.title !== '') {
                this.setState({ titleEditing: false })
              }
            }}
          />
        </div>
      )
    }
    let typeButton
    if (this.state.type === 'web_url') {
      typeButton = <ContentLink />
    } else if (this.state.type === 'postback') {
      typeButton = <ActionExitToApp />
    } else if (this.state.type === 'element_share') {
      typeButton = <SocialShare />
    }

    let configPopover

    if (this.state.type === 'web_url') {
      configPopover = (
        <Popover
          open={this.state.urlEditorOpen}
          anchorEl={this.config_anchorEl}
          anchorOrigin={{ horizontal: 'middle', vertical: 'center' }}
          targetOrigin={{ horizontal: 'left', vertical: 'top' }}
          onRequestClose={() => {
            if (this.validateUrl()) {
              this.setState({ urlEditorOpen: false, payload: undefined })
            }
          }}
        >
          <TextField
            hintText="Enter URL ..."
            errorText={this.state.urlEditorError}
            value={this.state.url}
            style={{ margin: '2px 7px' }}
            onChange={(e) => { this.setState({ url: e.target.value }) }}
            onKeyPress={(e) => {
              if (e.nativeEvent.code === 'Enter') {
                if (this.validateUrl()) {
                  this.setState({ urlEditorOpen: false, payload: undefined })
                }
              }
            }}
          />
        </Popover>
      )
    } else if (this.state.type === 'postback') {
      configPopover = (
        <Popover
          open={this.state.payloadEditorOpen}
          anchorEl={this.config_anchorEl}
          anchorOrigin={{ horizontal: 'middle', vertical: 'center' }}
          targetOrigin={{ horizontal: 'left', vertical: 'top' }}
          onRequestClose={() => {
            if (this.state.payload !== undefined) {
              this.setState({ payloadEditorOpen: false })
            }
          }}
        >
          <Menu>
            <MenuItem
              primaryText="A"
              onClick={() => {
                this.setState({
                  payload: {},
                  payloadEditorOpen: false,
                })
              }}
            />
            <MenuItem
              primaryText="B"
              onClick={() => {
                this.setState({
                  payload: {},
                  payloadEditorOpen: false,
                })
              }}
            />
          </Menu>
        </Popover>
      )
    }
    return (
      <div style={{ position: 'relative' }}>
        <ListItem
          primaryText={this.state.title}
          innerDivStyle={{ textAlign: 'center' }}
          onClick={() => {
            if (this.state.type !== 'element_share') {
              this.setState({ titleEditing: true })
            }
          }}
        />
        <FloatingActionButton
          mini
          onClick={(e) => {
            this.setState({
              typeMenuOpen: true,
              typeAnchorEl: e.currentTarget,
            })
          }}
          style={{ position: 'absolute', right: '46px', top: '3px' }}
        >
          {typeButton}
        </FloatingActionButton>
        <Popover
          open={this.state.typeMenuOpen}
          anchorEl={this.state.typeAnchorEl}
          anchorOrigin={{ horizontal: 'middle', vertical: 'center' }}
          targetOrigin={{ horizontal: 'left', vertical: 'top' }}
          onRequestClose={() => { this.setState({ typeMenuOpen: false }) }}
        >
          <Menu>
            <MenuItem
              primaryText="Link"
              checked={this.state.type === 'web_url'}
              insetChildren
              onClick={() => {
                this.setState({
                  type: 'web_url',
                  typeMenuOpen: false,
                  urlEditorOpen: true,
                })
              }}
            />
            <MenuItem
              primaryText="Action"
              checked={this.state.type === 'postback'}
              insetChildren
              onClick={() => {
                this.setState({
                  type: 'postback',
                  typeMenuOpen: false,
                  payloadEditorOpen: true,
                })
              }}
            />
            {!this.props.disableShare &&
            <MenuItem
              primaryText="Share"
              checked={this.state.type === 'element_share'}
              insetChildren
              onClick={() => {
                this.setState({
                  title: 'Share',
                  type: 'element_share',
                  typeMenuOpen: false,
                })
              }}
            />
            }
          </Menu>
        </Popover>

        <FloatingActionButton
          mini
          style={{ position: 'absolute', right: '3px', top: '3px' }}
          onClick={() => {
            if (this.state.type === 'web_url') {
              this.setState({ urlEditorOpen: true })
            } else if (this.state.type === 'postback') {
              this.setState({ payloadEditorOpen: true })
            }
          }}
          ref={(x) => {
            if (x) {
              this.config_anchorEl = x.refs.container.refs.enhancedButton
            }
          }}
          disabled={this.state.type === 'element_share'}
        >
          <ActionSettings />
        </FloatingActionButton>
        {configPopover}
      </div>
    )
  }
}

Button.propTypes = {
  disableShare: React.PropTypes.bool,
}

export default Button
