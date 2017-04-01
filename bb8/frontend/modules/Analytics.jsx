import storage from 'store2'
import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import Moment from 'moment'
import CircularProgress from 'material-ui/CircularProgress'
import DatePicker from 'material-ui/DatePicker'
import FlatButton from 'material-ui/FlatButton'
import Subheader from 'material-ui/Subheader'
import TextField from 'material-ui/TextField'
import Avatar from 'material-ui/Avatar'

import Diagrams from './Diagrams'

import { ACTIVE_BOT } from '../constants'
import * as uiActionCreators from '../actions/uiActionCreators'
import * as botActionCreators from '../actions/botActionCreators'

const CLIENT_ID = '791471658501-jdp3nf8jc1aueei26qhh73npe35r167o.apps.googleusercontent.com'

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
  loadingContainer: {
    justifyContent: 'center',
    alignItems: 'center',
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
  authButton: {
    margin: '0.5em',
    zIndex: 99,
  },
  hintContainer: {
    justifyContent: 'center',
    padding: '0 10vw',
    paddingBottom: '10vw',
  },
  hintText: {
    margin: '1.5em 0',
    fontSize: '.875em',
  },
  hintTextLink: {
    color: '#757575',
    fontSize: '.875em',
    padding: '.5em',
    margin: '-.5em 0',
    textDecoration: 'underline',
    cursor: 'pointer',
  },
}

class Analytics extends React.Component {
  constructor(props) {
    // load google analytics script
    const GA_EMBED_SCRIPT = 'ga-embed-script'
    if (!document.getElementById(GA_EMBED_SCRIPT)) {
      const script = document.createElement('script')

      script.id = GA_EMBED_SCRIPT
      script.text = `
        (function(w,d,s,g,js,fs){
          g=w.gapi||(w.gapi={});g.analytics={q:[],ready:function(f){this.q.push(f);}};
          js=d.createElement(s);fs=d.getElementsByTagName(s)[0];
          js.src='https://apis.google.com/js/platform.js';
          fs.parentNode.insertBefore(js,fs);js.onload=function(){g.load('analytics');};
        }(window,document,'script'))`
      document.body.appendChild(script)
    }

    super(props)
    this.handleStartDateChange = this.handleStartDateChange.bind(this)
    this.handleEndDateChange = this.handleEndDateChange.bind(this)
    this.handleGaIdInputChange = this.handleGaIdInputChange.bind(this)
    this.updateGaId = this.updateGaId.bind(this)
    this.loadViewIds = this.loadViewIds.bind(this)

    const now = new Date()
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setTime(now.getTime() - (1000 * 60 * 60 * 24 * 7))

    this.state = {
      startDate: sevenDaysAgo,
      endDate: now,
      datePickerOpen: false,
      gaIdInput: '',
      gaIdError: null,
      loading: true,
    }

    this.viewIdMapping = {}
  }

  componentDidMount() {
    // eslint-disable-next-line no-undef
    gapi.analytics.ready(() => {
      // eslint-disable-next-line no-undef
      if (!gapi.analytics.auth.isAuthorized()) {
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.authorize({
          container: 'embed-api-auth-container',
          clientid: CLIENT_ID,
        })
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.on('success', () => this.loadViewIds())
      } else {
        this.loadViewIds()
      }
    })
  }

  loadViewIds() {
    if (Object.keys(this.viewIdMapping).length >= 1) {
      return Promise.resolve(this.viewIdMapping)
    }
    // eslint-disable-next-line no-undef
    return gapi.client.analytics.management.accounts.list()
      .then(response =>
        Object.values(response.result.items).map(item => item.id))
      .then(accountIds => Promise.all(accountIds.map(accountId =>
        // eslint-disable-next-line no-undef
        gapi.client.analytics.management.webproperties.list({ accountId }))))
      .then(responses =>
        responses.map(resp =>
          Object.assign({},
            ...Object.values(resp.result.items)
                               .map(item => ({
                                 [item.id]: item.defaultProfileId,
                               })))
        )
      )
      .then(responses => Object.assign({}, ...responses))
      .then((mapping) => {
        this.viewIdMapping = mapping
        this.setState({ loading: false })
        return mapping
      })
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
    if (this.state.loading) {
      return (
        <div
          style={{ ...styles.container, ...styles.loadingContainer }}
        >
          <div
            id="embed-api-auth-container"
            style={{
              ...styles.authButton,
              display: 'none',
            }}
          />
          <CircularProgress
            size={30}
            thickness={3}
          />
        </div>
      )
    }

    if (!validateGaId(this.props.gaId)) {
      return (
        <div
          style={{
            ...styles.container,
            ...styles.hintContainer,
          }}
        >
          <div style={{ fontSize: '3em', color: '#BCBCBC' }}>
            :-(
          </div>
          <div>
            <TextField
              hintText="UA-98765432-1"
              floatingLabelText="TrackingID"
              errorText={this.state.gaIdError}
              onChange={this.handleGaIdInputChange}
            />
            <FlatButton
              label="Update"
              primary
              onTouchTap={this.updateGaId}
              style={{ margin: '0 1em' }}
            />
          </div>
          <p style={styles.hintText}>
            Please tell us your Google Analytics Tracking ID so we can track the data for you!
          </p>
          <div>
            <Avatar> ? </Avatar>
            <a
              href="//support.google.com/analytics/answer/1032385"
              style={styles.hintTextLink}
            >
              How to get your Google Analytics Tracking ID
            </a>
          </div>
        </div>
      )
    }

    const viewId = this.viewIdMapping[this.props.gaId]
    if (!viewId) {
      return (
        <div
          style={{
            ...styles.container,
            ...styles.hintContainer,
          }}
        >
          <div style={{ fontSize: '3em', color: '#BCBCBC' }}>
            :-(
          </div>
          <div
            id="embed-api-auth-container"
            style={styles.authButton}
          />
          <p style={styles.hintText}>
            Your Google account is not authorized to access the
            Google Analytics trackingID: {this.props.gaId}
            Please contact the administrator of your Google Analytics account.
          </p>
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
          viewId={viewId}
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
    gaId: getGaId(state.entities.bots, storage.get(ACTIVE_BOT)),
    bot: state.entities.bots[storage.get(ACTIVE_BOT)],
  }),
)(Analytics)

export default ConnectedAnalytics
