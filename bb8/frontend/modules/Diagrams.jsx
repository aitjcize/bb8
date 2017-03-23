import React from 'react'
import CircularProgress from 'material-ui/CircularProgress'
import Paper from 'material-ui/Paper'

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    flex: 1,
    padding: '1em .5em',
  },
  loader: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  rows: {
    display: 'flex',
    padding: '.5em 1em',
    marginBottom: '1em',
  },
  item: {
    flex: 1,
    marginBottom: '1.5em',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  tableContainer: {
    marginLeft: '1.5em',
  },
  authButton: {
    margin: '0.5em',
    zIndex: 99,
  }
}

const drawDiagram = (startDate, endDate, viewId, callback) => {
  if (!viewId) return

  const gaViewId = `ga:${viewId}`

  const pieDefaultOption = {
    width: '100%',
    height: 400,
    pieHole: 5 / 9,
    sliceVisibilityThreshold: 0.1,
    backgroundColor: 'transparent',
    chartArea: {
      left: 16,
      right: 16,
      top: 16,
      bottom: 16,
    },
    legend: {
      position: 'labeled',
    },
  }

  const tableDefaultOption = {
    width: '100%',
    cssClassNames: {
      headerRow: 'ga-table-headerRow',
      tableRow: 'ga-table-tableRow',
      oddTableRow: 'ga-table-oddTableRow',
      selectedTableRow: 'ga-table-selectedTableRow',
      hoverTableRow: 'ga-table-hoverTableRow',
      headerCell: 'ga-table-headerCell',
      tableCell: 'ga-table-tableCell',
      rowNumberCell: 'ga-table-rowNumberCell',
    },
  }

  const lineDefaultOption = {
    width: '100%',
    height: 350,
    backgroundColor: 'transparent',
    chartArea: {
      left: 16,
      right: 16,
    },
  }

  // eslint-disable-next-line no-undef
  const userTypePie = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:users',
      dimensions: 'ga:userType',
    },
    chart: {
      container: 'user-type-pie',
      type: 'PIE',
      options: pieDefaultOption,
    },
  })
  userTypePie.execute()

  // eslint-disable-next-line no-undef
  const userTypeTable = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:users',
      dimensions: 'ga:userType',
      'max-results': 7,
    },
    chart: {
      container: 'user-type-table',
      type: 'TABLE',
      options: {
        width: '100%',
        cssClassNames: {
          headerRow: 'ga-table-headerRow',
          tableRow: 'ga-table-tableRow',
          oddTableRow: 'ga-table-oddTableRow',
          selectedTableRow: 'ga-table-selectedTableRow',
          hoverTableRow: 'ga-table-hoverTableRow',
          headerCell: 'ga-table-headerCell',
          tableCell: 'ga-table-tableCell',
          rowNumberCell: 'ga-table-rowNumberCell',
        },
      },
    },
  })
  userTypeTable.execute()

  // eslint-disable-next-line no-undef
  const userSessionLine = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:users, ga:sessions',
      dimensions: 'ga:date',
    },
    chart: {
      container: 'user-session-line',
      type: 'LINE',
      options: lineDefaultOption,
    },
  })
  userSessionLine.execute()

  // eslint-disable-next-line no-undef
  const userSessionTable = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:newusers,ga:pageviews',
      dimensions: 'ga:date',
      sort: '-ga:date',
      'max-results': 10,
    },
    chart: {
      container: 'user-session-table',
      type: 'TABLE',
      options: {
        width: '100%',
        cssClassNames: {
          headerRow: 'ga-table-headerRow',
          tableRow: 'ga-table-tableRow',
          oddTableRow: 'ga-table-oddTableRow',
          selectedTableRow: 'ga-table-selectedTableRow',
          hoverTableRow: 'ga-table-hoverTableRow',
          headerCell: 'ga-table-headerCell',
          tableCell: 'ga-table-tableCell',
          rowNumberCell: 'ga-table-rowNumberCell',
        },
      },
    },
  })
  userSessionTable.execute()

  // eslint-disable-next-line no-undef
  const eventCategoryPie = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:users',
      dimensions: 'ga:eventCategory',
    },
    chart: {
      container: 'event-catagory-pie',
      type: 'PIE',
      options: pieDefaultOption,
    },
  })
  eventCategoryPie.execute()

  // eslint-disable-next-line no-undef
  const eventCategoryTable = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:users',
      dimensions: 'ga:eventCategory',
      'max-results': 10,
    },
    chart: {
      container: 'event-catagory-table',
      type: 'TABLE',
      options: tableDefaultOption,
    },
  })
  eventCategoryTable.execute()

  // eslint-disable-next-line no-undef
  const pagePathPie = new gapi.analytics.googleCharts.DataChart({
    query: {
      ids: gaViewId,
      'start-date': startDate,
      'end-date': endDate,
      metrics: 'ga:pageviews',
      dimensions: 'ga:pagePath',
      sort: '-ga:pageviews',
      'max-results': 5,
    },
    chart: {
      container: 'pagepath-pie',
      type: 'PIE',
      options: pieDefaultOption,
    },
  })
  pagePathPie.execute()

  // eslint-disable-next-line no-undef
  const pagePathTable = new gapi.analytics.googleCharts.DataChart({
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
      container: 'pagepath-table',
      type: 'TABLE',
      options: tableDefaultOption,
    },
  })
  pagePathTable.execute()

  userTypePie.on('success', callback)
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
    this.state = { startDate, endDate, gaId, loading: true }

    this.loadMapping = this.loadMapping.bind(this)
    this.mapping = {}
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
        })
        // eslint-disable-next-line no-undef
        gapi.analytics.auth.on('success', () => {
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
    drawDiagram(this.state.startDate, this.state.endDate, this.state.viewId, () => {
      this.setState({ loading: false })
    })
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
      <div
        style={styles.container}
      >
        <div id="embed-api-auth-container" style={styles.authButton} />
        {
        this.state.loading ? <div style={styles.loader}>
          <CircularProgress thickness={5} />
        </div> : null
        }
        <Paper style={styles.rows}>
          <div id="user-session-line" style={styles.item} />
          <div
            id="user-session-table"
            style={{
              ...styles.item,
              ...styles.tableContainer,
              ...{ flex: 'none' },
            }}
          />
        </Paper>
        <Paper style={styles.rows}>
          <div style={styles.item}>
            <div id="user-type-pie" />
            <div
              id="user-type-table"
              style={styles.tableContainer}
            />
          </div>
          <div style={styles.item}>
            <div id="event-catagory-pie" />
            <div id="event-catagory-table" style={styles.tableContainer} />
          </div>
        </Paper>
        <Paper style={styles.rows}>
          <div id="pagepath-pie" style={styles.item} />
          <div
            id="pagepath-table"
            style={{
              ...styles.item,
              ...styles.tableContainer,
            }}
          />
        </Paper>
      </div>
    )
  }
}

Diagrams.propTypes = {
  gaId: React.PropTypes.string,
  startDate: React.PropTypes.string,
  endDate: React.PropTypes.string,
}

export default Diagrams
