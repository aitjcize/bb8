import React from 'react'

import {
  Card,
  CardText,
  CardHeader,
  CardTitle,
  CardActions,
} from 'material-ui/Card'

import MenuItem from 'material-ui/MenuItem'
import Divider from 'material-ui/Divider'
import TextField from 'material-ui/TextField'
import SelectField from 'material-ui/SelectField'
import FlatButton from 'material-ui/FlatButton'

import {
  CarouselMessage,
  // eslint-disable-next-line no-unused-vars
  ImageMessage,
  // eslint-disable-next-line no-unused-vars
  TextCardMessage,
} from './Message'


const styles = {
  container: {
  },
  cardText: {
    paddingRight: '3em',
    paddingBottom: '3em',
  },
  header: {
    lineHeight: '1.5em',
    margin: '1em 0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  textFieldInput: {
    padding: '0 1em',
    boxSizing: 'border-box',
    textAlign: 'center',
  },
  errorMessageContainer: {
    margin: '1em',
    maxWidth: '50%',
  },
  errorMessageInputContainer: {
    display: 'flex',
    alignItems: 'center',
    padding: '0 .5em',
    boxSizing: 'border-box',
  },
  errorMessageInputField: {
    marginLeft: '.25em',
  },
  formWrapper: {
    width: '50%',
    display: 'flex',
    flexDirection: 'column',
  },
  formRow: {
    display: 'flex',
  },
}

class LandingPage extends React.Component {

  constructor(props) {
    super(props)

    this.state = {
      intro: '',
      content: [
        {
          requestText: 'Feature',
          type: 'carousel',
        },
        {
          requestText: 'Demo',
          type: 'carousel',
        },
        {
          requestText: 'Product',
          type: 'carousel',
        },
      ],
      errorMessage: [{}, {}, {}, {}, {}],
    }
  }

  render() {
    const { content, errorMessage } = this.state
    const introMaxLength = 150

    return (
      <Card
        expandable
        initiallyExpanded
        style={styles.container}
      >
        <CardHeader
          title="Quick Start"
          subtitle="subtitle"
        />
        <CardTitle
          title="Intro"
          subtitle="a simple welcome message to tell your costomer who you are."
        />
        <CardText
          style={styles.cardText}
        >
          <div
            style={{
              ...styles.formWrapper,
              ...{ alignItems: 'flex-end' },
            }}
          >
            <TextField
              multiLine
              rows={3}
              value={this.state.intro}
              fullWidth
              onChange={(e) => {
                if (e.target.value.length <= introMaxLength) {
                  this.setState({ intro: e.target.value })
                }
              }}
            />
            <span
              style={{
                color: '#bbb',
                fontStyle: 'italic',
                padding: '0 1.5em',
              }}
            >
              {`${this.state.intro.length}/${introMaxLength}`}
            </span>
          </div>
        </CardText>
        <Divider />
        <CardTitle
          title="Content"
          subtitle="description"
          showExpandableButton
          actAsExpander
        />
        <CardText
          expandable
          style={styles.cardText}
        >
          {
          content.map((b, idx) => (
            <div style={styles.items} key={idx}>
              <div style={styles.header}>
                <div>
                  When customer says
                  <TextField
                    value={this.state.content[idx].requestText}
                    inputStyle={styles.textFieldInput}
                    style={{ width: 'auto', minWidth: '10em' }}
                  />
                  ,
                  <br />
                  Do response:
                </div>
                <div>
                  <SelectField
                    floatingLabelText="Card Type"
                    value={1}
                    style={{ width: 'auto' }}
                    labelStyle={{ paddingRight: '1.5em', margin: '0 3em' }}
                  >
                    <MenuItem value={1} primaryText="Text Card" />
                    <MenuItem value={2} primaryText="Image" />
                    <MenuItem value={3} primaryText="Carousel" />
                    <Divider />
                    <MenuItem value={null} primaryText="Disable" />
                  </SelectField>
                </div>
              </div>
              <CarouselMessage />
            </div>
          ))
          }
        </CardText>
        <Divider />
        <CardTitle
          title="Contacts"
          subtitle="how do your customers reach you"
        />
        <CardText
          style={styles.cardText}
        >
          <div style={styles.formWrapper}>
            <div style={styles.formRow}>
              <TextField
                floatingLabelText="Business name"
                fullWidth
              />
            </div>
            <div style={styles.formRow}>
              <TextField
                floatingLabelText="Email"
                fullWidth
              />
              <TextField
                floatingLabelText="Phone number"
                fullWidth
              />
            </div>
            <div style={styles.formRow}>
              <TextField
                floatingLabelText="Open hour"
                fullWidth
              />
              <TextField
                floatingLabelText="Website"
                fullWidth
              />
            </div>
          </div>
        </CardText>
        <Divider />
        <CardTitle
          title="Error messages"
          subtitle="description"
        />
        <CardText
          style={styles.cardText}
        >
          <div style={styles.formWrapper}>
            {
            errorMessage.map((b, idx) => (
              <div key={idx} style={styles.errorMessageInputContainer}>
                <span style={{ fontStyle: 'italic', color: '#bbb' }}>
                  {`${idx + 1}. `}
                </span>
                <TextField
                  fullWidth
                  style={styles.errorMessageInputField}
                />
              </div>
            ))
            }
          </div>
        </CardText>
        <CardActions>
          <FlatButton
            label="save"
          />
        </CardActions>
      </Card>
    )
  }
}

export default LandingPage
