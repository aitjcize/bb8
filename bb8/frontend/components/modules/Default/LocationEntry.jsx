import React from 'react'

import Chip from 'material-ui/Chip'
import { amber200 } from 'material-ui/styles/colors'


class LocationEntry extends React.Component {
  constructor(props) {
    super(props)

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)
    this.valid = this.valid.bind(this)

    this.state = {
      type: 'location',
    }
  }

  valid() {
    return this.state.type === 'location'
  }

  toJSON() {
    return {
      type: this.state.type,
    }
  }

  fromJSON() {
    this.setState({ type: 'location' })
  }

  render() {
    const styles = {
      chip: {
        margin: '0.5em 0.25em',
      },
      wrapper: {
        display: 'flex',
        flexWrap: 'wrap',
      },
    }
    return (
      <div>
        <div style={styles.wrapper}>
          <Chip
            backgroundColor={amber200}
            style={styles.chip}
          >
            Location Message
          </Chip>
        </div>
      </div>
    )
  }
}

export default LocationEntry
