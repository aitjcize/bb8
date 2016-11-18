import React from 'react'

const drawDiagram = (startDate, endDate, viewId) => {
  if (!viewId) return

  const gaViewId = `ga:${viewId}`

  // eslint-disable-next-line no-undef
  const dataChart1 = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:sessions',
      dimensions: 'ga:date',
    },
    chart: {
      container: 'chart-1-container',
      type: 'LINE',
      options: {
        width: '100%',
      },
    },
  })
  dataChart1.execute()

  // eslint-disable-next-line no-undef
  const dataChart2 = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:users',
      dimensions: 'ga:eventCategory',
    },
    chart: {
      container: 'chart-2-container',
      type: 'LINE',
      options: {
        width: '100%',
      },
    },
  })
  dataChart2.execute()

  // eslint-disable-next-line no-undef
  const dataChart3 = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:pageviews',
      dimensions: 'ga:pagePath',
      sort: '-ga:pageviews',
      'max-results': 10,
    },
    chart: {
      container: 'chart-3-container',
      type: 'PIE',
      options: {
        width: '100%',
        pieHole: 3 / 9,
      },
    },
  })
  dataChart3.execute()

  // eslint-disable-next-line no-undef
  const dataChart4 = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:pageviews,ga:uniquePageviews',
      dimensions: 'ga:pagePath',
      sort: '-ga:pageviews',
      'max-results': 10,
    },
    chart: {
      container: 'chart-4-container',
      type: 'TABLE',
    },
  })
  dataChart4.execute()

  // eslint-disable-next-line no-undef
  const dataChart5 = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:newUsers',
      dimensions: 'ga:date',
    },
    chart: {
      container: 'chart-5-container',
      type: 'LINE',
      options: {
        width: '100%',
      },
    },
  })
  dataChart5.execute()

  // eslint-disable-next-line no-undef
  const dataChart6 = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:pageViews',
      dimensions: 'ga:date',
    },
    chart: {
      container: 'chart-6-container',
      type: 'LINE',
      options: {
        width: '100%',
      },
    },
  })
  dataChart6.execute()
}

const CLIENT_ID = '791471658501-jdp3nf8jc1aueei26qhh73npe35r167o.apps.googleusercontent.com'

class Diagrams extends React.Component {

  constructor(props) {
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
    const { startDate, endDate, gaId } = this.props
    this.state = { startDate, endDate, gaId }

    this.loadMapping = this.loadMapping.bind(this)
    this.mapping = {}
  }

  componentDidMount() {
    const gaId = this.state.gaId

    // eslint-disable-next-line no-undef
    gapi.analytics.ready(() => {
      // eslint-disable-next-line no-undef
      if (!gapi.analytics.auth.isAuthorized()) {
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.authorize({
          container: 'embed-api-auth-container',
          clientid: CLIENT_ID,
          userInfoLabel: '',
        })
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.on('success', () => {
          document.getElementById('embed-api-auth-container').style.display = 'none'
          this.loadMapping().then(mapping => this.setState({ viewId: mapping[gaId] }))
        })
      } else {
        this.loadMapping().then(mapping => this.setState({ viewId: mapping[gaId] }))
      }
    })
  }

  componentWillReceiveProps(props) {
    const { startDate, endDate, gaId } = props
    this.setState({ startDate, endDate, gaId })

    // eslint-disable-next-line no-undef
    gapi.analytics.ready(() => {
      // eslint-disable-next-line no-undef
      if (!gapi.analytics.auth.isAuthorized()) {
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.authorize({
          container: 'embed-api-auth-container',
          clientid: CLIENT_ID,
          userInfoLabel: '',
        })
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.on('success', () => {
          document.getElementById('embed-api-auth-container').style.display = 'none'
          this.loadMapping().then(mapping => this.setState({ viewId: mapping[gaId] }))
        })
      } else {
        this.loadMapping().then(mapping => this.setState({ viewId: mapping[gaId] }))
      }
    })
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.state.startDate === prevState.startDate &&
        this.state.endDate === prevState.endDate &&
        this.state.viewId === prevState.viewId) {
      return
    }
    drawDiagram(this.state.startDate, this.state.endDate, this.state.viewId)
  }

  loadMapping() {
    if (Object.keys(this.mapping).length >= 1) {
      return Promise.resolve(this.mapping)
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
          Object.assign({}, ...Object.values(resp.result.items)
                                     .map(item => ({
                                       [item.id]: item.defaultProfileId,
                                     })))
        )
      )
      .then(responses => Object.assign({}, ...responses))
      .then((mapping) => {
        this.mapping = mapping
        return mapping
      })
  }

  render() {
    return (
      <div>
        <div id="embed-api-auth-container" />
        <div id="chart-1-container" />
        <div id="chart-2-container" />
        <div id="chart-3-container" />
        <div id="chart-4-container" />
        <div id="chart-5-container" />
        <div id="chart-6-container" />
        <div id="chart-7-container" />
      </div>)
  }
}

Diagrams.propTypes = {
  gaId: React.PropTypes.string,
  startDate: React.PropTypes.string,
  endDate: React.PropTypes.string,
}

export default Diagrams
