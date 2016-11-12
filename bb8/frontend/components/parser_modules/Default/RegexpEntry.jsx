import React from 'react'

import Chip from 'material-ui/Chip'
import Snackbar from 'material-ui/Snackbar'
import TextField from 'material-ui/TextField'
import { lightBlue100 } from 'material-ui/styles/colors'


const maxParams = 20


class RegexpEntry extends React.Component {
  constructor(props) {
    super(props)

    this.toJSON = this.toJSON.bind(this)
    this.fromJSON = this.fromJSON.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
    this.valid = this.valid.bind(this)

    this.state = {
      value: '',
      type: 'regexp',
      params: [],
      snackbarOpen: false,
      snackbarMessage: '',
    }
  }

  valid() {
    return this.state.params.length > 0
  }

  toJSON() {
    return {
      type: 'regexp',
      params: this.state.params,
    }
  }

  fromJSON(data) {
    this.setState({ params: data.params })
  }

  handleSubmit() {
    if (this.state.value !== '') {
      if (this.state.params.length === maxParams) {
        this.setState({
          snackbarOpen: true,
          snackbarMessage: 'Maximun number of patterns reached!',
        })
        return
      }
      this.setState(prevState => ({
        value: '',
        params: prevState.params.concat([this.state.value]),
      }))
    }
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
          {
          this.state.params.map((param, index) => (
            <Chip
              key={param}
              backgroundColor={lightBlue100}
              style={styles.chip}
              onRequestDelete={() => {
                this.setState((prevState) => {
                  const params = prevState.params
                  params.splice(index, 1)
                  return { params }
                })
              }}
            >
              {param}
            </Chip>
          ))
          }
          <TextField
            value={this.state.value}
            onChange={(e) => { this.setState({ value: e.target.value }) }}
            onKeyPress={(e) => {
              if (e.nativeEvent.code === 'Enter') {
                this.handleSubmit()
              }
            }}
            style={{ marginLeft: '0.5em' }}
          />
        </div>
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

export default RegexpEntry
