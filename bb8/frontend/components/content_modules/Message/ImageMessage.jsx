import React from 'react'

import { Card, CardText, CardMedia } from 'material-ui/Card'
import TextField from 'material-ui/TextField'

import Styles from './Styles'


class ImageMessage extends React.Component {
  constructor(props) {
    super(props)

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)

    this.state = { url: 'http://i.imgur.com/4loi6PJ.jpg' }

    this.defaultProps = {
      readOnly: false,
    }
  }

  valid() {
    return this.state.url
  }

  fromJSON(msg) {
    this.setState({ url: msg.attachment.payload.url })
  }

  toJSON() {
    return {
      attachment: {
        type: 'image',
        payload: { url: this.state.url },
      },
    }
  }

  render() {
    const valid = /^(http|https):\/\/[^ "]+$/.test(this.state.url)
    return (
      <div>
        <Card style={Styles.card}>
          {valid &&
            <CardMedia>
              <img alt="message" src={this.state.url} />
            </CardMedia>
          }
          <CardText>
            <TextField
              floatingLabelText="Image URL"
              value={this.state.url}
              onChange={(e) => {
                if (!this.props.readOnly) {
                  this.setState({ url: e.target.value })
                }
              }}
            />
          </CardText>
        </Card>
      </div>
    )
  }
}

ImageMessage.propTypes = {
  readOnly: React.PropTypes.bool,
}


export default ImageMessage
