import React from 'react'

import Divider from 'material-ui/Divider'
import FlatButton from 'material-ui/FlatButton'
import Menu from 'material-ui/Menu'
import MenuItem from 'material-ui/MenuItem'
import Paper from 'material-ui/Paper'
import Popover from 'material-ui/Popover'
import TextField from 'material-ui/TextField'

import RegexpEntry from './RegexpEntry'
import LocationEntry from './LocationEntry'


class Rule extends React.Component {
  constructor(props) {
    super(props)

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)
    this.valid = this.valid.bind(this)

    this.state = {
      nodes: ['A', 'B', 'C'],
      ackMessage: '',
      endNodeId: null,
      endNodeIdEditorOpen: false,
      endNodeIdEditorAnchorEl: undefined,
    }
    this.entry = undefined
  }

  valid() {
    return (this.entry.valid() &&
            (!!this.state.ackMessage || !!this.state.endNodeId))
  }

  toJSON() {
    return {
      rule: this.entry.toJSON(),
      ack_message: this.state.ackMessage,
      end_node_id: this.state.endNodeId,
    }
  }

  fromJSON(data) {
    this.setState({
      ackMessage: data.ack_message,
      endNodeId: data.end_node_id,
    })
    this.entry.fromJSON(data.rule)
  }

  render() {
    let entry
    if (this.props.type === 'regexp') {
      entry = <RegexpEntry ref={(r) => { this.entry = r }} />
    } else if (this.props.type === 'location') {
      entry = <LocationEntry ref={(r) => { this.entry = r }} />
    }
    const labelStyle = {
      margin: '0.3em',
    }
    return (
      <div>
        <Paper style={{ padding: '0.5em' }}>
          {entry}
          <div style={{ display: 'flex' }}>
            <span style={labelStyle}>Reply</span>
            <div>
              <TextField
                value={this.state.ackMessage}
                onChange={(e) => { this.setState({ ackMessage: e.target.value }) }}
              />
            </div>
            <span style={labelStyle}>Goto</span>
            <div>
              <FlatButton
                label={this.state.endNodeId || 'Choose'}
                onClick={(e) => {
                  this.setState({
                    endNodeIdEditorOpen: true,
                    endNodeIdEditorAnchorEl: e.currentTarget,
                  })
                }}
              />
              <Popover
                open={this.state.endNodeIdEditorOpen}
                anchorEl={this.state.endNodeIdEditorAnchorEl}
                onRequestClose={() => {
                  this.setState({ endNodeIdEditorOpen: false })
                }}
              >
                <Menu>
                  <MenuItem
                    primaryText="Clear"
                    onClick={() => {
                      this.setState({
                        endNodeId: null,
                        endNodeIdEditorOpen: false,
                      })
                    }}
                  />
                  <Divider />
                  {
                  this.state.nodes.map(node => (
                    <MenuItem
                      primaryText={node}
                      onClick={() => {
                        this.setState({
                          endNodeId: node,
                          endNodeIdEditorOpen: false,
                        })
                      }}
                    />
                  ))
                  }
                </Menu>
              </Popover>
            </div>
          </div>
        </Paper>
      </div>
    )
  }
}

Rule.propTypes = {
  type: React.PropTypes.string.isRequired,
}

export default Rule
