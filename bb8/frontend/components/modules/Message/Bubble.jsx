import React from 'react'
import uniqueId from 'lodash/uniqueId'

import { Card, CardText, CardMedia } from 'material-ui/Card'
import Divider from 'material-ui/Divider'
import TextField from 'material-ui/TextField'
import FlatButton from 'material-ui/FlatButton'
import List from 'material-ui/List'

import Button from './Button'
import Styles from './Styles'

import LogoSvg from '../../../assets/logoLight.svg'

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
  },
  cover: {
    paddingTop: '52.63%', // 1:1.9
    position: 'relative',
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'center',
    backgroundSize: 'cover',
  },
  emptyCover: {
    backgroundImage: `url(${LogoSvg})`,
    backgroundSize: 'contain',
  },
  coverActionContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, .2)',
    transition: '.24s ease-out',
  },
  coverAction: {
    display: 'flex',
    flexDirection: 'column',
  },
}

class Bubble extends React.Component {

  constructor(props) {
    super(props)

    this.onRemoveClicked = this.onRemoveClicked.bind(this)
    this.addButton = this.addButton.bind(this)
    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.state = {
      title: '',
      subtitle: '',

      imageUrl: '',

      itemUrl: '',
      itemUrlEditorOpen: false,
      itemUrlEditorError: '',
      itemUrlEditorAnchorEl: undefined,

      buttonIds: [],

      hoverIndex: undefined,
      coverHover: false,

      addButtonTextEditing: false,
      addButtonTextBuffer: '',
    }
    this.buttons = {}
    this.idBut = {}

    this.defaultProps = {
      disableShare: false,
      readOnly: false,
    }
  }

  onRemoveClicked(id) {
    this.setState(prevState => (
      { buttonIds: prevState.buttonIds.filter(x => x !== id) }
    ))
    delete this.buttons[id]
  }

  addButton(title) {
    if (this.state.buttonIds.length < 3) {
      const id = uniqueId('buttons_message')
      this.idBut[id] = {
        type: undefined,
        title,
        url: '',
      }
      this.setState(prevState => (
        { buttonIds: prevState.buttonIds.concat([id]) }
      ))
    }
  }

  loadFromJSON(button, id) {
    this.buttons[id] = button
    if (this.idBut[id]) {
      button.fromJSON(this.idBut[id])
      delete this.idBut[id]
    }
  }

  validateUrl(urlInput, validation) {
    const valid = /^(http|https):\/\/[^ "]+$/.test(urlInput)
    const stateObj = {}

    stateObj[validation] = (!urlInput || valid) ? undefined : 'Invalid URL'

    this.setState(stateObj)

    return valid
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
      <Card
        style={Styles.card}
      >
        <CardMedia
          onMouseEnter={() => { this.setState({ coverHover: true }) }}
          onMouseLeave={() => { this.setState({ coverHover: false }) }}
        >
          <div
            style={{
              ...styles.cover,
              ...!this.state.imageUrl ? styles.emptyCover : {},
              ...this.state.imageUrl && {
                backgroundImage: `url(${this.state.imageUrl})`,
              },
            }}
          >
            <div
              style={{
                ...styles.coverActionContainer,
                ...{ opacity: (this.state.coverHover || !this.state.imageUrl) ? 1 : 0 },
              }}
            >
              <div
                style={styles.coverAction}
              >
                <TextField
                  hintText={!this.state.imageUrlTextFieldFocused && 'Image URL'}
                  inputStyle={{
                    color: 'white',
                    textAlign: 'center',
                  }}
                  hintStyle={{
                    color: 'white',
                    textAlign: 'center',
                    width: '100%',
                    textTransform: 'capitalize',
                  }}
                  underlineFocusStyle={{
                    borderColor: 'white',
                  }}
                  errorText={this.state.imageUrlEditorError}
                  value={this.state.imageUrlTextFieldBuffer}
                  onChange={(e) => {
                    this.setState({
                      imageUrlTextFieldBuffer: e.target.value,
                    })
                    this.validateUrl(this.state.imageUrlTextFieldBuffer, 'imageUrlEditorError')
                  }}
                  onKeyPress={(e) => {
                    if (e.nativeEvent.which === 13) {
                      this.setState({
                        imageUrlTextFieldFocused: false,
                        imageUrl: this.validateUrl(this.state.imageUrlTextFieldBuffer, 'imageUrlEditorError') ? this.state.imageUrlTextFieldBuffer : undefined,
                      })
                      e.target.blur()
                    }
                  }}
                  onFocus={(e) => {
                    this.setState({
                      imageUrlTextFieldFocused: true,
                    })
                    e.target.select()
                  }}
                  onBlur={() => {
                    this.setState({
                      imageUrlTextFieldFocused: false,
                      imageUrl: this.validateUrl(this.state.imageUrlTextFieldBuffer, 'imageUrlEditorError') ? this.state.imageUrlTextFieldBuffer : undefined,
                    })
                  }}
                />
                {this.state.imageUrl && <FlatButton
                  label="remove"
                  labelStyle={{ color: 'white' }}
                  onClick={() => {
                    this.setState({
                      imageUrl: undefined,
                      imageUrlTextFieldBuffer: '',
                    })
                  }}
                />}
              </div>
            </div>
          </div>
        </CardMedia>
        {this.state.imageUrl && <Divider />}
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
            style={{
              height: '2.5em',
              lineHeight: '2.5em',
            }}
            hintStyle={{
              bottom: 0,
            }}
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
            style={{
              fontSize: '1em',
              height: '2.5em',
              lineHeight: '2.5em',
            }}
            hintStyle={{
              bottom: 0,
            }}
          />
        </CardText>
        <List>
          <div>
            {this.state.buttonIds.map((id, index) => (
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
                <Divider />
                <Button
                  readOnly={this.props.readOnly}
                  ref={(b) => { this.loadFromJSON(b, id) }}
                  onRemoveClicked={() => { this.onRemoveClicked(id) }}
                />
              </div>
            ))}
            {!this.props.readOnly && showAddButton && (
              <div>
                <Divider />
                <TextField
                  fullWidth
                  underlineShow={false}
                  value={this.state.addButtonTextBuffer}
                  hintText={!this.state.addButtonTextEditing && 'New Button'}
                  inputStyle={{ textAlign: 'center' }}
                  hintStyle={{
                    textAlign: 'center',
                    width: '100%',
                    color: '#29D3A4',
                  }}
                  onChange={(e) => {
                    this.setState({ addButtonTextBuffer: e.target.value })
                  }}
                  onFocus={() => {
                    this.setState({ addButtonTextEditing: true })
                  }}
                  onBlur={() => {
                    if (this.state.addButtonTextBuffer) {
                      this.addButton(this.state.addButtonTextBuffer)
                    }
                    this.setState({
                      addButtonTextEditing: false,
                      addButtonTextBuffer: '',
                    })
                  }}
                  onKeyPress={(e) => {
                    if (e.nativeEvent.code === 'Enter' && e.target.value) {
                      this.addButton(this.state.addButtonTextBuffer)
                      this.setState({
                        addButtonTextEditing: this.state.buttonIds.length < 2,
                        addButtonTextBuffer: '',
                      })
                    }
                  }}
                />
              </div>
            )}
          </div>
        </List>
      </Card>
    )
  }
}

Bubble.propTypes = {
  readOnly: React.PropTypes.bool,
}

export default Bubble
