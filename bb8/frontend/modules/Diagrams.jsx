import React from 'react'
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
}

function drawDiagram(startDate, endDate, viewId) {
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
}

class Diagrams extends React.Component {

  componentDidMount() {
    const { startDate, endDate, viewId } = this.props
    drawDiagram(startDate, endDate, viewId)
  }

  componentDidUpdate(prevProps) {
    if (this.props.startDate === prevProps.startDate &&
        this.props.endDate === prevProps.endDate &&
        this.props.viewId === prevProps.viewId) {
      return
    }
    const { startDate, endDate, viewId } = this.props
    drawDiagram(startDate, endDate, viewId)
  }

  render() {
    return (
      <div
        style={styles.container}
      >
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
  viewId: React.PropTypes.string.isRequired,
  startDate: React.PropTypes.string.isRequired,
  endDate: React.PropTypes.string.isRequired,
}

export default Diagrams
