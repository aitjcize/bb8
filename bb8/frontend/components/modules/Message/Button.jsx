import React from 'react'

import IconRemoveCircle from 'material-ui/svg-icons/content/remove-circle'
import IconChevronRight from 'material-ui/svg-icons/navigation/chevron-right'
import IconShare from 'material-ui/svg-icons/social/share'
import IconLink from 'material-ui/svg-icons/content/link'
import IconLinearScale from 'material-ui/svg-icons/editor/linear-scale'

import Popover from 'material-ui/Popover'
import TextField from 'material-ui/TextField'
import { List, ListItem } from 'material-ui/List'
import FlatButton from 'material-ui/FlatButton'
import IconButton from 'material-ui/IconButton'
import Subheader from 'material-ui/Subheader'
import Divider from 'material-ui/Divider'

const styles = {
  listItemInnerDiv: {
    padding: 0,
    display: 'flex',
    alignItems: 'center',
  },
  deleteButton: {
    overflow: 'hidden',
    display: 'flex',
    justifyContent: 'flex-end',
    width: 0,
    padding: 0,
    opacity: 0,
    transform: 'scale(.5)',
    transition: '.15s',
  },
  deleteButtonHover: {
    width: '1em',
    padding: '0 0 0 1em',
    opacity: 1,
    transform: 'scale(1)',
    transition: '.24s .15s ease-out',
  },
  deleteButtonIconContainer: {
    padding: 0,
    width: 'auto',
    height: 'auto',
    cursor: 'pointer',
  },
  actionMenuPopoverScrollArea: {
    overflowY: 'scroll',
    maxHeight: '30vh',
  },
}

class Button extends React.Component {

  constructor(props) {
    super(props)

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)
    this.clearState = this.clearState.bind(this)

    this.clearState()
    this.configAnchorEl = undefined

    this.defaultProps = {
      disableShare: false,
      readOnly: false,
    }
    this.state = {
      actionMenuOpen: false,
    }
  }

  clearState() {
    this.state = {
      // type: 'web_url',
      type: undefined,
      // typeMenuOpen: false,
      // typeAnchorEl: undefined,

      title: '',
      titleEditing: true,

      url: '',
      urlEditorOpen: false,
      urlEditorError: undefined,

      payload: undefined,
      // payloadEditorOpen: false,
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
    if (!this.state.url) {
      this.setState({ urlEditorError: 'Please enter a url of this picture' })
      return false
    } else if (!valid && this.state.url !== '') {
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
        title: 'Share',
      }
    }
    return {}
  }

  fromJSON(msg) {
    this.clearState()
    this.setState({ titleEditing: false, ...msg })
    // if (msg.type === 'element_share') {
      // this.setState({ title: 'Share' })
    // }
  }

  render() {
    const actionMenuPopover = (<Popover
      open={this.state.actionMenuOpen}
      anchorEl={this.state.actionMenuAnchorEl}
      anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      targetOrigin={{ horizontal: 'left', vertical: 'center' }}
      onRequestClose={() => this.setState({ actionMenuOpen: false })}
      style={{
        minWidth: '15vw',
      }}
    >
      <List>
        <Subheader>Choose Action</Subheader>
        <div
          style={styles.actionMenuPopoverScrollArea}
        >
          {['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'].map((b, i) => (
            <ListItem
              key={i}
              primaryText={`Action ${b}`}
              style={{
                fontSize: '.875em',
                textTransform: 'capitalize',
              }}
              onClick={() => {
                this.setState({
                  type: 'postback',
                  payload: {},
                  actionMenuOpen: false,
                })
              }}
            />
            ))}
        </div>
      </List>
      <Divider />
      <List>
        <ListItem
          primaryText="Share"
          onClick={() => {
            this.setState({
              type: 'element_share',
              actionMenuOpen: false,
            })
          }}
        />
        <ListItem
          primaryText="Open link"
          onClick={() => {
            this.setState({
              type: 'web_url',
              urlEditorOpen: true,
              actionMenuOpen: false,
            })
          }}
        />
      </List>
    </Popover>)

    return (
      <ListItem
        innerDivStyle={styles.listItemInnerDiv}
        onMouseEnter={() => this.setState({ hover: true })}
        onMouseLeave={() => this.setState({ hover: false })}
      >
        <div
          style={{
            ...styles.deleteButton,
            ...(!this.state.titleEditing && !this.state.urlEditorOpen && this.state.hover) ||
            this.state.titleEditing ? styles.deleteButtonHover : {},
          }}
        >
          <IconButton
            style={styles.deleteButtonIconContainer}
            onClick={this.props.onRemoveClicked}
          >
            <IconRemoveCircle />
          </IconButton>
        </div>
        {
        !this.state.urlEditorOpen && <TextField
          hintText="Button title"
          value={this.state.type === 'element_share' ? 'Share' : this.state.title}
          underlineShow={false}
          disabled={this.state.type === 'element_share'}
          onFocus={() => {
            this.setState({ titleEditing: true })
          }}
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
          style={{
            flex: 1,
            margin: '0 1em',
          }}
        />
        }
        {
        this.state.type === 'web_url' && <TextField
          hintText="http://"
          value={this.state.url}
          ref="urlEditorTextField"
          underlineShow={false}
          autoFocus={this.state.urlEditorOpen}
          onChange={(e) => { this.setState({ url: e.target.value }) }}
          onFocus={() => this.setState({ urlEditorOpen: true })}
          onBlur={() => this.setState({ urlEditorOpen: false })}
          onKeyPress={(e) => {
            if (e.nativeEvent.code === 'Enter') {
              if (this.validateUrl()) {
                this.setState({ urlEditorOpen: false, payload: undefined })
              }
            }
          }}
          style={{
            ...{
              flex: 2,
              margin: '0 1em',
            },
            ...!this.state.urlEditorOpen ? {
              fontSize: '.875em',
            } : {},
          }}
          inputStyle={{
            ...!this.state.urlEditorOpen ? { color: '#BBBBBB' } : {},
            ...this.state.urlEditorError ? { color: 'red' } : {},
          }}
        />
        }
        <div>
          {
          this.state.titleEditing || this.state.urlEditorOpen ? <FlatButton
            label="done"
            hoverColor="transparent"
            rippleColor="transparent"
            style={{ margin: '0 .5em' }}
            onClick={() => this.setState({ urlEditorOpen: false, titleEditing: false })}
          /> : <div
            onClick={(e) => {
              this.setState({
                actionMenuOpen: true,
                actionMenuAnchorEl: e.currentTarget,
                hover: false,
              })
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '0 .5em',
            }}
          >
            {
            !this.state.type && <FlatButton
              label="actions"
              labelPosition="before"
              hoverColor="transparent"
              rippleColor="transparent"
              labelStyle={{ color: '#BBBBBB' }}
            />
            }
            {
            this.state.type === 'postback' && <IconButton>
              <IconLinearScale />
            </IconButton>
            }
            {
            this.state.type === 'element_share' && <IconButton>
              <IconShare />
            </IconButton>
            }
            {
            this.state.type === 'web_url' && <IconButton
              tooltip={this.state.url ? this.state.url : false}
              tooltipPosition="top-right"
            >
              <IconLink />
            </IconButton>
            }
            <IconChevronRight
              style={{ marginLeft: '-.5em' }}
            />
          </div>
          }
        </div>
        {actionMenuPopover}
      </ListItem>
    )
  }
}

Button.propTypes = {
  disableShare: React.PropTypes.bool,
  readOnly: React.PropTypes.bool,
  onRemoveClicked: React.PropTypes.func,
}

export default Button
