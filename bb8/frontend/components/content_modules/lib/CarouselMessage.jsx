import React from 'react'
import uniqueId from 'lodash/uniqueId'

import { Card } from 'material-ui/Card'
import ContentAdd from 'material-ui/svg-icons/content/add'
import ActionDelete from 'material-ui/svg-icons/action/delete'
import FloatingActionButton from 'material-ui/FloatingActionButton'

import Bubble from './Bubble'


class CarouselMessage extends React.Component {
  constructor(props) {
    super(props)

    this.onAddClicked = this.onAddClicked.bind(this)
    this.onRemoveClicked = this.onRemoveClicked.bind(this)
    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.state = {
      bubbleIds: [uniqueId('bubbles_message')],
      hoverIndex: undefined,
    }
    this.bubbles = {}
    this.maxBubbles = 7
    this.idBub = {}
  }

  onAddClicked() {
    if (this.state.bubbleIds.length < this.maxBubbles) {
      this.setState(prevState => (
        { bubbleIds: prevState.bubbleIds.concat(
          [uniqueId('bubbles_message')]) }
      ))
    }
  }

  onRemoveClicked(id) {
    this.setState(prevState => (
      { bubbleIds: prevState.bubbleIds.filter(x => x !== id) }
    ))
    delete this.bubbles[id]
  }

  loadFromJSON(bubble, id) {
    this.bubbles[id] = bubble
    if (this.idBub[id]) {
      bubble.fromJSON(this.idBub[id])
      delete this.idBub[id]
    }
  }

  valid() {
    return this.state.bubbleIds.length > 0
  }

  fromJSON(msg) {
    const bubbles = msg.attachment.payload.elements
    const idBub = {}
    const bubbleIds = []
    for (const bub of bubbles) {
      const id = uniqueId('bubbles_message')
      idBub[id] = bub
      bubbleIds.push(id)
    }
    this.setState({ bubbleIds })
    this.idBub = idBub
  }

  toJSON() {
    const bubbles = []
    for (const id of this.state.bubbleIds) {
      if (this.bubbles[id].valid()) {
        bubbles.push(this.bubbles[id].toJSON())
      }
    }
    return {
      attachment: {
        type: 'template',
        payload: {
          template_type: 'generic',
          elements: bubbles,
        },
      },
    }
  }

  render() {
    const showAddButton = this.state.bubbleIds.length < this.maxBubbles
    return (
      <div
        style={{
          maxHeight: '450px',
          minHeight: '354px',
          height: '100%',
          maxWidth: this.props.maxWidth,
          overflowX: 'auto',
          overflowY: 'hidden',
          whiteSpace: 'nowrap',
        }}
      >
        {
        this.state.bubbleIds.map((id, index) => (
          <div
            key={id}
            style={{
              width: this.props.editorWidth,
              position: 'relative',
              display: 'inline-block',
              verticalAlign: 'top',
              margin: '3px',
              whiteSpace: 'normal',
            }}
            onMouseEnter={() => { this.setState({ hoverIndex: index }) }}
            onMouseLeave={() => { this.setState({ hoverIndex: undefined }) }}
          >
            <Bubble
              editorWidth={this.props.editorWidth}
              ref={(b) => { this.loadFromJSON(b, id) }}
            />
            {((index !== 0 || this.state.bubbleIds.length > 1) &&
              this.state.hoverIndex === index) &&
              <FloatingActionButton
                mini
                secondary
                onClick={() => { this.onRemoveClicked(id) }}
                style={{ position: 'absolute', right: '10px', top: '3px' }}
              >
                <ActionDelete />
              </FloatingActionButton>
            }
          </div>
        ))
        }
        {showAddButton && (
        <Card
          style={{
            width: '80px',
            height: '100%',
            minHeight: '296px',
            position: 'relative',
            display: 'inline-block',
            verticalAlign: 'top',
            margin: '3px',
          }}
        >
          <div
            style={{
              position: 'absolute',
              verticalAlign: 'middle',
              horizontalAlign: 'center',
              display: 'inline-block',
              top: 'calc(50% - 20px)',
              left: '20px',
            }}
          >
            <FloatingActionButton
              mini
              secondary
              onClick={() => { this.onAddClicked() }}
            >
              <ContentAdd />
            </FloatingActionButton>
          </div>
        </Card>
        )}
      </div>
    )
  }
}


CarouselMessage.propTypes = {
  maxWidth: React.PropTypes.string,
  editorWidth: React.PropTypes.string.isRequired,
}

export default CarouselMessage
