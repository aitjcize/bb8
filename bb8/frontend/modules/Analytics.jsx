import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import Moment from 'moment'
import DatePicker from 'material-ui/DatePicker'
import FlatButton from 'material-ui/FlatButton'
import Subheader from 'material-ui/Subheader'
import TextField from 'material-ui/TextField'

import Diagrams from './Diagrams'

import * as uiActionCreators from '../actions/uiActionCreators'
import * as botActionCreators from '../actions/botActionCreators'

const formatDate = date => Moment(date).format('YYYY-MM-DD')

const validateGaId = gaId => /^(UA|YT|MO)-\d+-\d+$/i.test(gaId)

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    boxSizing: 'border-box',
    minHeight: '100%',
    padding: '1em',
  },
  header: {
    display: 'flex',
    justifyContent: 'flex-end',
    backgroundColor: '#EEEEEE',
    zIndex: 1,
  },
  datePicker: {
    minWidth: '12em',
    width: '10vw',
  },
  datePickerInput: {
    boxSizing: 'border-box',
    textAlign: 'center',
    position: 'relative',
    fontStyle: 'italic',
  },
  label: {
    margin: '0 1em 0 2em',
    textTransform: 'capitalize',
  },
}

class Analytics extends React.Component {
  constructor(props) {
    super(props)
    this.handleStartDateChange = this.handleStartDateChange.bind(this)
    this.handleEndDateChange = this.handleEndDateChange.bind(this)
    this.handleGaIdInputChange = this.handleGaIdInputChange.bind(this)
    this.updateGaId = this.updateGaId.bind(this)

    const now = new Date()
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setTime(now.getTime() - (1000 * 60 * 60 * 24 * 7))
    this.state = {
      startDate: sevenDaysAgo,
      endDate: now,
      datePickerOpen: false,
      gaIdInput: '',
      gaIdError: null,
    }
  }

  handleStartDateChange(e, startDate) {
    this.setState({ startDate })
  }

  handleEndDateChange(e, endDate) {
    this.setState({ endDate })
  }

  handleGaIdInputChange(e, gaId) {
    const valid = validateGaId(gaId)
    this.setState({
      gaIdInput: gaId,
      gaIdError: (valid || !gaId) ? null : 'Please enter a valid Google Analytcis trackingID',
    })
  }

  updateGaId() {
    const uiActions = bindActionCreators(
      uiActionCreators, this.props.dispatch)
    const botActions = bindActionCreators(
      botActionCreators, this.props.dispatch)

    if (this.state.gaIdError) {
      uiActions.openNotification('Please enter a correct trackingID')
    } else {
      botActions.updateBot(this.props.bot.id, {
        bot: {
          name: this.props.bot.name,
          description: this.props.bot.description,
          gaId: this.state.gaIdInput,
        },
      })
    }
  }

  render() {
    if (!validateGaId(this.props.gaId)) {
      return (
        <div>
          <p> Please tell us your Google Analytics Tracking ID so we can track the data for you </p>
          <p> Here is how to get your Google Analytics Tracking ID: https://support.google.com/analytics/answer/1032385 </p>

          <div>
            <TextField
              hintText="UA-41575341-1"
              floatingLabelText="Google Analytics TrackingID"
              errorText={this.state.gaIdError}
              onChange={this.handleGaIdInputChange}
            />
            <FlatButton
              label="Update trackID"
              primary
              onTouchTap={this.updateGaId}
            />
          </div>
        </div>
      )
    }

    return (
      <div
        style={styles.container}
      >
        <Subheader
          style={styles.header}
        >
          <span style={styles.label}>from</span>
          <DatePicker
            autoOk
            hintText="Pick a start date"
            value={this.state.startDate}
            onChange={this.handleStartDateChange}
            inputStyle={styles.datePickerInput}
            style={styles.datePicker}
            fullWidth
            formatDate={() => Moment(this.state.startDate).format('ll')}
          />
          <span style={styles.label}>to</span>
          <DatePicker
            autoOk
            hintText="Pick an end date"
            value={this.state.endDate}
            onChange={this.handleEndDateChange}
            inputStyle={styles.datePickerInput}
            style={styles.datePicker}
            fullWidth
            formatDate={() => Moment(this.state.endDate).format('ll')}
          />
        </Subheader>
        <Diagrams
          gaId={this.props.gaId}
          startDate={formatDate(this.state.startDate)}
          endDate={formatDate(this.state.endDate)}
        />
      </div>
    )
  }
}

Analytics.propTypes = {
  gaId: React.PropTypes.string,
  dispatch: React.PropTypes.func.isRequired,
  bot: React.PropTypes.shape({
    id: React.PropTypes.number.isRequired,
    name: React.PropTypes.string.isRequired,
    description: React.PropTypes.string.isRequired,
  }),
}

const getGaId = (bots, activeId) => {
  const bot = bots[activeId]
  if (bot) {
    return bot.gaId
  }
  return ''
}

const ConnectedAnalytics = connect(
  state => ({
    gaId: getGaId(state.entities.bots, state.bots.active),
    bot: state.entities.bots[state.bots.active],
  }),
)(Analytics)

export default ConnectedAnalytics
