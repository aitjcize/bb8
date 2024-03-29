import storage from 'store2'
import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import Moment from 'moment'
import CircularProgress from 'material-ui/CircularProgress'
import DatePicker from 'material-ui/DatePicker'
import FlatButton from 'material-ui/FlatButton'
import RaisedButton from 'material-ui/RaisedButton'
import Subheader from 'material-ui/Subheader'
import TextField from 'material-ui/TextField'

import Diagrams from './Diagrams'

import { ACTIVE_BOT } from '../constants'
import * as uiActionCreators from '../actions/uiActionCreators'
import * as botActionCreators from '../actions/botActionCreators'

const CLIENT_ID = '791471658501-jdp3nf8jc1aueei26qhh73npe35r167o.apps.googleusercontent.com'
const OAUTH_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

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
  emptyContainer: {
    margin: '3em 3em',
  },
  loadingContainer: {
    width: '100%',
    marginTop: '30%',
    textAlign: 'center',
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
    this.authCallback = this.authCallback.bind(this)
    this.handleAuthentication = this.handleAuthentication.bind(this)
    this.handleEndDateChange = this.handleEndDateChange.bind(this)
    this.handleGaIdInputChange = this.handleGaIdInputChange.bind(this)
    this.handleStartDateChange = this.handleStartDateChange.bind(this)
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
    gapi.load('client:auth2', () => {
      // eslint-disable-next-line no-undef
      gapi.client.init({
        clientId: CLIENT_ID,
        scope: OAUTH_SCOPE,
      }).then(() => {
        // eslint-disable-next-line no-undef
        const authInstance = gapi.auth2.getAuthInstance()
        const user = authInstance.currentUser.get()
        const isAuthorized = user.hasGrantedScopes(OAUTH_SCOPE)

        if (isAuthorized) {
          this.setState({ unauthorized: false })
          this.authCallback(true)
        } else {
          this.setState({ unauthorized: true })
          authInstance.isSignedIn.listen(this.authCallback)
        }
      })
    })
  }

  authCallback(isSignedIn) {
    // eslint-disable-next-line no-undef
    const token = gapi.auth2.getAuthInstance().currentUser.get().getAuthResponse().access_token
    // eslint-disable-next-line no-undef
    gapi.analytics.ready(() => {
      if (isSignedIn) {
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.authorize({
          serverAuth: {
            access_token: token,
          },
        })
        this.setState({ unauthorized: false })
        this.loadViewIds()
        return
      }
      this.setState({ unauthorized: true, loading: false })
    })
  }

  loadViewIds() {
    this.setState({ loading: true })
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

  handleAuthentication() {
    if (!this.state.unauthorized) {
      return
    }
    // eslint-disable-next-line no-undef
    gapi.auth2.getAuthInstance().signIn()
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
          style={styles.loadingContainer}
        >
          <CircularProgress
            size={80}
            thickness={5}
          />
        </div>
      )
    }

    if (this.state.unauthorized) {
      return (
        <div
          style={styles.authButton}
        >
          You have not logined to the Google Analytics yet, please click this button to login
          <div>
            <RaisedButton
              style={{
                margin: '1em',
              }}
              onClick={() => {
                this.handleAuthentication()
              }}
              label="Authorize"
            />
          </div>
        </div>
      )
    }

    if (!validateGaId(this.props.gaId)) {
      return (
        <div style={styles.emptyContainer}>
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

    const viewId = this.viewIdMapping[this.props.gaId]
    if (!viewId) {
      return (
        <div style={styles.emptyContainer}>
          <p> Your Google account is not authorized to access the
            Google Analytics trackingID: {this.props.gaId}
          </p>
          <p> Please contact the administrator of your Google Analytics account. </p>
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
