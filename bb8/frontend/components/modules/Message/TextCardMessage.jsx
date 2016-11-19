import React from 'react'
import uniqueId from 'lodash/uniqueId'

import { Card, CardText } from 'material-ui/Card'
import ActionDelete from 'material-ui/svg-icons/action/delete'
import Divider from 'material-ui/Divider'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import { List } from 'material-ui/List'
import TextField from 'material-ui/TextField'

import Button from './Button'
import Styles from './Styles'

const styles = {
  container: {
    display: 'flex',
  },
  info: {
    flex: 1,
    borderRadius: 0,
    boxShadow: 'none',
  },
}


class TextCardMessage extends React.Component {
  constructor(props) {
    super(props)

    this.onRemoveClicked = this.onRemoveClicked.bind(this)
    this.addButton = this.addButton.bind(this)
    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.state = {
      text: '',
      buttonIds: [],
      hoverIndex: undefined,

      addButtonTextEditing: false,
      addButtonTextBuffer: '',
    }
    this.buttons = {}
    this.idBut = {}

    this.defaultProps = {
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
        type: 'web_url',
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

  valid() {
    return !!this.state.text
  }

  fromJSON(msg) {
    if (msg.text) {
      this.setState({ text: msg.text })
    } else {
      const buttons = msg.attachment.payload.buttons
      const idBut = {}
      const buttonIds = []
      for (const but of buttons) {
        const id = uniqueId('buttons_message')
        idBut[id] = but
        buttonIds.push(id)
      }
      this.setState({ buttonIds })
      this.idBut = idBut
      this.setState({ text: msg.attachment.payload.text })
    }
  }

  toJSON() {
    if (this.state.buttonIds.length > 0) {
      const buttons = []
      for (const id of this.state.buttonIds) {
        if (this.buttons[id].valid()) {
          buttons.push(this.buttons[id].toJSON())
        }
      }
      return {
        attachment: {
          type: 'template',
          payload: {
            template_type: 'button',
            text: this.state.text,
            buttons,
          },
        },
      }
    }
    return { text: this.state.text }
  }

  render() {
    const showAddButton = this.state.buttonIds.length < 3
    return (
      <div style={styles.container}>
        <Card
          style={{
            ...Styles.card,
            ...this.props.editorWidth && { width: this.props.editorWidth },
          }}
        >
          <CardText>
            <TextField
              hintText="Text to send"
              value={this.state.text}
              underlineShow={false}
              fullWidth
              multiLine
              onChange={(e) => {
                if (!this.props.readOnly) {
                  this.setState({ text: e.target.value })
                }
              }}
            />
          </CardText>
          <List>
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
                <Divider />
                <Button
                  disableShare
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
              </div>
            ))
            }
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
                onBlur={(e) => {
                  if (e.target.value) {
                    this.addButton(e.target.addButtonTextBuffer)
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
          </List>
        </Card>
        {/*
        <Card style={styles.info}>
          <CardTitle
            title="Text Card"
            subtitle="a card with text and actions!"
          />
          <CardText>
          </CardText>
        </Card>
        */}
      </div>
    )
  }
}

TextCardMessage.propTypes = {
  editorWidth: React.PropTypes.string,
  readOnly: React.PropTypes.bool,
}


export default TextCardMessage
