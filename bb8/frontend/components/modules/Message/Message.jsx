import React from 'react'
import uniqueId from 'lodash/uniqueId'

import { Validator } from 'jsonschema'

import Snackbar from 'material-ui/Snackbar'
import { Card } from 'material-ui/Card'
import { List, ListItem } from 'material-ui/List'
import Subheader from 'material-ui/Subheader'

import TextCardMessage from './TextCardMessage'
import CarouselMessage from './CarouselMessage'
import ImageMessage from './ImageMessage'
import ButtonGroup from './ButtonGroup'
import Styles from './Styles'

import ModuleInfos from '../../../constants/ModuleInfos.json'

const styles = {
  container: {
    padding: '1.5em',
    display: 'flex',
    flexDirection: 'column',
    borderRadius: 0,
    boxShadow: 'none',
  },
  messageContainer: {
    flex: 1,
    position: 'relative',
    marginBottom: '1em',
  },
}


class Message extends React.Component {
  constructor(props) {
    super(props)

    this.moduleId = 'ai.compose.content.core.message'

    this.onAddClicked = this.onAddClicked.bind(this)
    this.onRemoveClicked = this.onRemoveClicked.bind(this)
    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)
    this.loadFromJSON = this.loadFromJSON.bind(this)

    this.state = {
      messageInfos: [],
      snackbarOpen: false,
      snackbarMessage: '',
      hoverIndex: undefined,
    }
    this.messages = {}
    this.idMsg = {}

    this.defaultProps = {
      maxMessages: 3,
      editorWidth: '18.75em',
      readOnly: false,
    }
  }

  onAddClicked(type) {
    if (this.state.messageInfos.length < this.props.maxMessages) {
      this.setState(prevState => (
        { messageInfos: prevState.messageInfos.concat(
          [{ id: uniqueId('messages'), type }]) }
      ))
    }
  }

  onRemoveClicked(id) {
    this.setState(prevState => (
      { messageInfos: prevState.messageInfos.filter(x => x.id !== id) }
    ))
    delete this.messages[id]
  }

  clear() {
    this.messages = {}
    this.idMsg = {}
    this.setState({
      messageInfos: [],
      snackbarOpen: false,
      snackbarMessage: '',
      hoverIndex: undefined,
    })
  }

  loadFromJSON(message, id) {
    this.messages[id] = message
    if (this.idMsg[id]) {
      message.fromJSON(this.idMsg[id])
      delete this.idMsg[id]
    }
  }

  fromJSON(msgs) {
    const idMsg = {}
    const messageInfos = []
    for (const msg of msgs.messages) {
      const id = uniqueId('messages')
      idMsg[id] = msg
      let type = 'TextCardMessage'
      if (msg.attachment) {
        if (msg.attachment.type === 'image') {
          type = 'ImageMessage'
        } else if (msg.attachment.payload.template_type === 'generic') {
          type = 'CarouselMessage'
        }
      }
      messageInfos.push({ id, type })
    }
    this.setState({ messageInfos })
    this.idMsg = idMsg
  }

  toJSON() {
    const messages = []
    for (const info of this.state.messageInfos) {
      if (this.messages[info.id].valid()) {
        messages.push(this.messages[info.id].toJSON())
      }
    }
    const v = new Validator()
    const schema = ModuleInfos[this.moduleId].schema
    const result = v.validate({ messages }, schema)
    if (!result.valid) {
      this.setState({
        snackbarOpen: true,
        snackbarMessage: 'Critial: message validation failed',
      })
    }
    return { messages }
  }

  render() {
    const showAddButton = (!this.props.readOnly &&
      this.state.messageInfos.length < this.props.maxMessages)


    return (
      <div style={styles.container}>
        {
        this.state.messageInfos.map((info, index) => {
          let messageContent

          if (info.type === 'TextCardMessage') {
            messageContent = (
              <TextCardMessage
                editorWidth={this.props.editorWidth}
                readOnly={this.props.readOnly}
                ref={(m) => { this.loadFromJSON(m, info.id) }}
              />
            )
          } else if (info.type === 'ImageMessage') {
            messageContent = (
              <ImageMessage
                editorWidth={this.props.editorWidth}
                readOnly={this.props.readOnly}
                ref={(m) => { this.loadFromJSON(m, info.id) }}
              />
            )
          } else if (info.type === 'CarouselMessage') {
            messageContent = (
              <CarouselMessage
                editorWidth={this.props.editorWidth}
                readOnly={this.props.readOnly}
                ref={(m) => { this.loadFromJSON(m, info.id) }}
              />
            )
          }

          return (
            <div
              key={info.id}
              onMouseEnter={() => {
                this.setState({ hoverIndex: index })
              }}
              onMouseLeave={() => {
                this.setState({ hoverIndex: undefined })
              }}
              style={styles.messageContainer}
            >
              {messageContent}
              {!this.props.readOnly &&
                info.type !== 'CarouselMessage' &&
                <ButtonGroup
                  onRemoveClicked={() => { this.onRemoveClicked(info.id) }}
                />
              }
            </div>
          )
        })
        }
        {showAddButton &&
        <Card style={Styles.card}>
          <List>
            <Subheader>
              New message
            </Subheader>
            <ListItem
              primaryText="Text Card"
              onClick={() => { this.onAddClicked('TextCardMessage') }}
            />
            <ListItem
              primaryText="Image"
              onClick={() => { this.onAddClicked('ImageMessage') }}
            />
            <ListItem
              primaryText="Carousel"
              onClick={() => { this.onAddClicked('CarouselMessage') }}
            />
          </List>
        </Card>
        }
        <Snackbar
          open={this.state.snackbarOpen}
          message={this.state.snackbarMessage}
          autoHideDuration={3000}
          onRequestClose={() => { this.setState({ snackbarOpen: false }) }}
        />
      </div>
    )
  }
}

Message.propTypes = {
  maxMessages: React.PropTypes.number.isRequired,
  editorWidth: React.PropTypes.string,
  readOnly: React.PropTypes.bool,
}

export default Message
