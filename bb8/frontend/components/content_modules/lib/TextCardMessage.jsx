import React from 'react'
import Lodash from 'lodash'

import { Card, CardText, CardMedia } from 'material-ui/Card'
import ActionDelete from 'material-ui/svg-icons/action/delete'
import Divider from 'material-ui/Divider'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import { ListItem } from 'material-ui/List'
import TextField from 'material-ui/TextField'

import Button from './Button'


class TextCardMessage extends React.Component {
  constructor(props) {
    super(props)

    this.onAddClicked = this.onAddClicked.bind(this)
    this.onRemoveClicked = this.onRemoveClicked.bind(this)
    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.state = {
      text: '',
      buttonIds: [],
      hoverIndex: undefined,
    }
    this.buttons = {}
    this.idBut = {}
  }

  onAddClicked() {
    if (this.state.buttonIds.length < 3) {
      this.setState(prevState => (
        { buttonIds: prevState.buttonIds.concat(
          [Lodash.uniqueId('buttons_message')]) }
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
        const id = Lodash.uniqueId('buttons_message')
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
      <Card style={{ width: this.props.editorWidth }}>
        <CardText>
          <TextField
            hintText="Text to send"
            value={this.state.text}
            underlineShow={false}
            fullWidth
            multiLine
            onChange={(e) => { this.setState({ text: e.target.value }) }}
            inputStyle={{ fontWeight: '600' }}
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
                  disableShare
                  ref={(b) => { this.loadFromJSON(b, id) }}
                />
                {this.state.hoverIndex === index &&
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
            {showAddButton && (
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

TextCardMessage.propTypes = {
  editorWidth: React.PropTypes.string.isRequired,
}


export default TextCardMessage
