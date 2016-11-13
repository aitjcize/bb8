import React from 'react'
import uniqueId from 'lodash/uniqueId'

import { Card, CardText, CardMedia } from 'material-ui/Card'
import ActionDelete from 'material-ui/svg-icons/action/delete'
import ContentLink from 'material-ui/svg-icons/content/link'
import FileUpload from 'material-ui/svg-icons/file/file-upload'
import Divider from 'material-ui/Divider'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import { ListItem } from 'material-ui/List'
import Popover from 'material-ui/Popover'
import TextField from 'material-ui/TextField'

import Button from './Button'


class Bubble extends React.Component {

  constructor(props) {
    super(props)

    this.onAddClicked = this.onAddClicked.bind(this)
    this.onRemoveClicked = this.onRemoveClicked.bind(this)
    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.state = {
      title: '',
      subtitle: '',

      imageUrl: 'http://i.imgur.com/4loi6PJ.jpg',
      imageUrlEditorOpen: false,
      imageUrlEditorError: '',
      imageUrlEditorAnchorEl: undefined,

      itemUrl: '',
      itemUrlEditorOpen: false,
      itemUrlEditorError: '',
      itemUrlEditorAnchorEl: undefined,

      buttonIds: [],

      hoverIndex: undefined,
    }
    this.buttons = {}
    this.idBut = {}

    this.defaultProps = {
      disableShare: false,
      readOnly: false,
    }
  }

  onAddClicked() {
    if (this.state.buttonIds.length < 3) {
      this.setState(prevState => (
        { buttonIds: prevState.buttonIds.concat(
          [uniqueId('buttons')]) }
      ))
    }
  }

  onRemoveClicked(id) {
    this.setState(prevState => (
      { buttonIds: prevState.buttonIds.filter(x => x !== id) }
    ))
    delete this.buttons[id]
  }

  loadFromJSON(button, id) {
    this.buttons[id] = button
    if (this.idBut[id]) {
      button.fromJSON(this.idBut[id])
      delete this.idBut[id]
    }
  }

  validateUrl() {
    const valid = /^(http|https):\/\/[^ "]+$/.test(this.state.imageUrl)
    if (!valid) {
      this.setState({ imageUrlEditorError: 'Invalid URL' })
      return false
    }
    this.setState({ imageUrlEditorError: undefined })
    return true
  }

  valid() {
    if (!this.state.title) {
      return false
    }
    return true
  }

  fromJSON(msg) {
    const idBut = {}
    const buttonIds = []
    for (const but of msg.buttons) {
      const id = uniqueId('buttons')
      idBut[id] = but
      buttonIds.push(id)
    }
    this.setState({ buttonIds })
    this.setState({
      title: msg.title,
      subtitle: msg.subtitle,
      imageUrl: msg.image_url,
      itemUrl: msg.item_url,
    })
    this.idBut = idBut
  }

  toJSON() {
    const buttons = []
    for (const id of this.state.buttonIds) {
      if (this.buttons[id].valid()) {
        buttons.push(this.buttons[id].toJSON())
      }
    }
    return {
      title: this.state.title,
      subtitle: this.state.subtitle,
      item_url: this.state.itemUrl,
      image_url: this.state.imageUrl,
      buttons,
    }
  }

  render() {
    const showAddButton = this.state.buttonIds.length < 3
    return (
      <Card style={{ width: this.props.editorWidth }}>
        <CardMedia
          style={{
            width: '100%',
            height: '9.75em',
            overflow: 'hidden',
          }}
        >
          <img
            alt="cover"
            src={this.state.imageUrl}
            style={{
              width: this.props.editorWidth,
              position: 'absolute',
            }}
          />
        </CardMedia>
        {!this.props.readOnly &&
        <div>
          <FloatingActionButton
            mini
            onClick={(e) => {
              this.setState({
                imageUrlEditorOpen: true,
                imageUrlEditorAnchorEl: e.currentTarget,
              })
            }}
            style={{
              position: 'absolute',
              right: '0.2em',
              top: '6.9em',
            }}
          >
            <FileUpload />
          </FloatingActionButton>
          <Popover
            open={this.state.imageUrlEditorOpen}
            anchorEl={this.state.imageUrlEditorAnchorEl}
            anchorOrigin={{ horizontal: 'middle', vertical: 'center' }}
            targetOrigin={{ horizontal: 'left', vertical: 'top' }}
            onRequestClose={() => {
              if (this.validateUrl()) {
                this.setState({
                  imageUrlEditorOpen: false,
                })
              }
            }}
          >
            <TextField
              hintText="Enter image URL ..."
              errorText={this.state.imageUrlEditorError}
              value={this.state.imageUrl}
              onChange={(e) => { this.setState({ imageUrl: e.target.value }) }}
              onKeyPress={(e) => {
                if (e.nativeEvent.code === 'Enter') {
                  if (this.validateUrl()) {
                    this.setState({ imageUrlEditorOpen: false })
                  }
                }
              }}
              style={{ margin: '0.125em 0.5em' }}
            />
          </Popover>
          <FloatingActionButton
            mini
            onClick={(e) => {
              this.setState({
                itemUrlEditorOpen: true,
                itemUrlEditorAnchorEl: e.currentTarget,
              })
            }}
            style={{
              position: 'absolute',
              right: '2.875em',
              top: '6.9em',
            }}
          >
            <ContentLink />
          </FloatingActionButton>
          <Popover
            open={this.state.itemUrlEditorOpen}
            anchorEl={this.state.itemUrlEditorAnchorEl}
            anchorOrigin={{ horizontal: 'middle', vertical: 'center' }}
            targetOrigin={{ horizontal: 'left', vertical: 'top' }}
            onRequestClose={() => {
              if (this.validateUrl()) {
                this.setState({
                  itemUrlEditorOpen: false,
                })
              }
            }}
          >
            <TextField
              hintText="URL when image is clicked"
              errorText={this.state.itemUrlEditorError}
              value={this.state.itemUrl}
              onChange={(e) => { this.setState({ itemUrl: e.target.value }) }}
              onKeyPress={(e) => {
                if (e.nativeEvent.code === 'Enter') {
                  if (this.validateUrl()) {
                    this.setState({ itemUrlEditorOpen: false })
                  }
                }
              }}
              style={{ margin: '0.125em 0.5em' }}
            />
          </Popover>
        </div>
        }
        <CardText>
          <TextField
            hintText="Title"
            value={this.state.title}
            underlineShow={false}
            fullWidth
            onChange={(e) => {
              if (!this.props.readOnly) {
                this.setState({ title: e.target.value })
              }
            }}
            style={{ height: '2em' }}
            hintStyle={{ bottom: '0.25em' }}
            inputStyle={{ fontWeight: '700' }}
          />
          <TextField
            hintText="Subtitle"
            value={this.state.subtitle}
            underlineShow={false}
            fullWidth
            onChange={(e) => {
              if (!this.props.readOnly) {
                this.setState({ subtitle: e.target.value })
              }
            }}
            style={{ height: '1.75em' }}
            hintStyle={{ bottom: '0.125em', fontSize: '80%' }}
            inputStyle={{ fontSize: '80%', color: 'grey' }}
          />
        </CardText>
        <CardMedia>
          <div>
            <Divider />
            {
            this.state.buttonIds.map((id, index) => (
              <div
                key={id}
                style={{ position: 'relative' }}
                onMouseEnter={() => {
                  this.setState({ hoverIndex: index })
                }}
                onMouseLeave={() => {
                  this.setState({ hoverIndex: undefined })
                }}
              >
                <Button
                  readOnly={this.props.readOnly}
                  ref={(b) => { this.loadFromJSON(b, id) }}
                />
                {!this.props.readOnly && this.state.hoverIndex === index &&
                <FloatingActionButton
                  mini
                  secondary
                  onClick={() => { this.onRemoveClicked(id) }}
                  style={{ position: 'absolute', left: '0em', top: '0.2em' }}
                >
                  <ActionDelete />
                </FloatingActionButton>
                }
                <Divider />
              </div>
            ))
            }
            {!this.props.readOnly && showAddButton && (
            <ListItem
              primaryText="Add a button"
              onClick={this.onAddClicked}
            />
            )}
          </div>
        </CardMedia>
      </Card>
    )
  }
}

Bubble.propTypes = {
  editorWidth: React.PropTypes.string.isRequired,
  readOnly: React.PropTypes.bool,
}

export default Bubble