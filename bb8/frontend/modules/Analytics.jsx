import React from 'react'
import { connect } from 'react-redux'

import Moment from 'moment'
import DatePicker from 'material-ui/DatePicker'
import Subheader from 'material-ui/Subheader'

import Diagrams from './Diagrams'

const formatDate = date => Moment(date).format('YYYY-MM-DD')

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

    const now = new Date()
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setTime(now.getTime() - (1000 * 60 * 60 * 24 * 7))
    this.state = {
      startDate: sevenDaysAgo,
      endDate: now,
      datePickerOpen: false,
    }
  }

  handleStartDateChange(e, startDate) {
    this.setState({ startDate })
  }

  handleEndDateChange(e, endDate) {
    this.setState({ endDate })
  }

  render() {
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
}

const ConnectedAnalytics = connect(
  state => ({
    gaId: state.entities.bots[state.bots.active].gaId,
  }),
  () => ({}),
)(Analytics)

export default ConnectedAnalytics
