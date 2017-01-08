import React from 'react'
import uniqueId from 'lodash/uniqueId'

import ContentAdd from 'material-ui/svg-icons/content/add'
import FloatingActionButton from 'material-ui/FloatingActionButton'

import Bubble from './Bubble'
import ButtonGroup from './ButtonGroup'

const styles = {
  bubbleContainer: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
  },
}


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
    this.defaultProps = {
      readOnly: false,
    }
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
    if (this.state.bubbleIds.length === 0) {
      return false
    }

    for (const id of this.state.bubbleIds) {
      if (!this.bubbles[id].valid()) {
        return false
      }
    }
    return true
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
          display: 'flex',
          overflowX: 'scroll',
        }}
      >
        {
        this.state.bubbleIds.map((id, index) => (
          <div
            key={id}
            onMouseEnter={() => { this.setState({ hoverIndex: index }) }}
            onMouseLeave={() => { this.setState({ hoverIndex: undefined }) }}
            style={styles.bubbleContainer}
          >
            <Bubble
              readOnly={this.props.readOnly}
              ref={(b) => { this.loadFromJSON(b, id) }}
            />
            {!this.props.readOnly && <ButtonGroup
              onRemoveClicked={() => { this.onRemoveClicked(id) }}
            >
              <div
                style={{
                  textAlign: 'right',
                  padding: '0 .5em',
                }}
              >
                <span
                  style={{
                    color: '#B4B4B4',
                    padding: '0 .5em',
                  }}
                >
                  {`${index + 1}/${this.maxBubbles}`}
                </span>
                {index >= 7 && (
                  <span
                    style={{
                      fontSize: '.7em',
                    }}
                  >
                    This card may NOT show up on LINE platform.
                  </span>
                )}
              </div>
            </ButtonGroup>}
          </div>
        ))
        }
        {!this.props.readOnly && showAddButton &&
        <div
          style={{
          }}
        >
          <FloatingActionButton
            mini
            secondary
            onClick={() => { this.onAddClicked() }}
            style={{ margin: '1em', marginRight: '2.5em' }}
          >
            <ContentAdd />
          </FloatingActionButton>
        </div>
        }
      </div>
    )
  }
}

CarouselMessage.propTypes = {
  readOnly: React.PropTypes.bool,
}

export default CarouselMessage
