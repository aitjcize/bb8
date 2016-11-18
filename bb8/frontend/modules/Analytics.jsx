import React from 'react'
import { connect } from 'react-redux'

import Moment from 'moment'
import DatePicker from 'material-ui/DatePicker'

import Diagrams from './Diagrams'

const formatDate = date => Moment(date).format('YYYY-MM-DD')

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
      <div>
        <DatePicker
          autoOk
          hintText="Pick a start date"
          value={this.state.startDate}
          onChange={this.handleStartDateChange}
        />
        <DatePicker
          autoOk
          hintText="Pick an end date"
          value={this.state.endDate}
          onChange={this.handleEndDateChange}
        />
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
