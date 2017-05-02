import React from 'react'

import CircularProgress from 'material-ui/CircularProgress'
import Paper from 'material-ui/Paper'
import {
  Table,
  TableBody,
  TableHeader,
  TableHeaderColumn,
  TableRow,
  TableRowColumn,
} from 'material-ui/Table'
import Chart from 'chart.js'

import { numUsersQuery,
         numUsersByDateQuery,
         numNewUsersQuery,
         numNewUsersByDateQuery,
         sessionByDateQuery,
         popularBlocksQuery,
         popularInputsQuery } from './queries'

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    flex: 1,
    padding: '1em .5em',
  },
  overview: {
    container: {
      display: 'flex',
      justifyContent: 'flex-start',
      marginBottom: '1em',
    },
    item: {
      width: '40%',
      paddingLeft: '1em',
      marginRight: '1em',
    },
  },
}

function fetch(query) {
  return new Promise((resolve) => {
    // eslint-disable-next-line no-undef
    const apiQuery = new gapi.client.analytics.data.ga.get(query)
    apiQuery.execute((results) => {
      resolve(results)
    })
  })
}

class Diagrams extends React.Component {

  constructor(props) {
    super(props)
    this.drawDiagram = this.drawDiagram.bind(this)

    this.state = {
      loading: true,
      popularBlocks: [],
      popularInputs: [],
      numUsers: 0,
      numNewUsers: 0,
    }
  }

  componentDidMount() {
    const { startDate, endDate, viewId } = this.props
    this.drawDiagram(startDate, endDate, viewId)
      .then(() => {
        this.setState({ loading: false })
      })
  }

  componentDidUpdate(prevProps) {
    if (this.props.startDate === prevProps.startDate &&
        this.props.endDate === prevProps.endDate &&
        this.props.viewId === prevProps.viewId) {
      return
    }
    const { startDate, endDate, viewId } = this.props
    this.drawDiagram(startDate, endDate, viewId)
      .then(() => {
        this.setState({ loading: false })
      })
  }

  drawDiagram(startDate, endDate, viewId) {
    this.setState({ loading: true })

    const gaViewId = `ga:${viewId}`
    const promises = []

    promises.push(
      Promise.all([
        fetch(numUsersByDateQuery(gaViewId, startDate, endDate)),
        fetch(numNewUsersByDateQuery(gaViewId, startDate, endDate)),
        fetch(sessionByDateQuery(gaViewId, startDate, endDate)),
      ]).then((result) => {
        const result1 = result[0]
        const result2 = result[1]
        const result3 = result[2]

        // eslint-disable-next-line no-new
        new Chart('usageChart', {
          type: 'line',
          data: {
            labels: result1.rows.map(r => r[0]),
            datasets: [
              {
                label: 'number of users',
                fill: false,
                data: result1.rows.map(r => r[1]),
                borderColor: 'rgba(255, 0, 0, 0.3)',
              },
              {
                label: 'number of new users',
                fill: false,
                data: result2.rows.map(r => r[1]),
                borderColor: 'rgba(0, 255, 0, 0.3)',
              },
              {
                label: 'number of sessions',
                fill: false,
                data: result3.rows.map(r => r[1]),
                borderColor: 'rgba(0, 0, 255, 0.3)',
              },
            ],
          },
        })
      })
    )

    promises.push(
      Promise.all([
        fetch(popularBlocksQuery(gaViewId, startDate, endDate)),
        fetch(popularInputsQuery(gaViewId, startDate, endDate)),
      ]).then((result) => {
        const result1 = result[0].rows
        const result2 = result[1].rows
        this.setState({
          popularBlocks: result1,
          popularInputs: result2,
        })
      })
    )

    promises.push(
      Promise.all([
        fetch(numUsersQuery(gaViewId, startDate, endDate)),
        fetch(numNewUsersQuery(gaViewId, startDate, endDate)),
      ]).then((result) => {
        const numUsers = parseInt(result[0].rows[0][0], 10)
        const numNewUsers = parseInt(result[1].rows[0][0], 10)
        this.setState({
          numUsers, numNewUsers,
        })
      })
    )

    return Promise.all(promises)
  }

  render() {
    return (
      <div
        style={styles.container}
      >
        {
          this.state.loading &&
          <div
            style={{
              width: '100%',
              marginTop: '30%',
              textAlign: 'center',
            }}
          >
            <CircularProgress
              size={80}
              thickness={5}
            />
          </div>
        }
        <div
          style={{ display: this.state.loading ? 'none' : 'initial' }}
        >
          <div
            style={styles.overview.container}
          >
            <Paper
              style={styles.overview.item}
            >
              <h5> Number of New Users </h5>
              <h5> { this.state.numNewUsers } </h5>
            </Paper>
            <Paper
              style={styles.overview.item}
            >
              <h5> Number of Active Users </h5>
              <h5> { this.state.numUsers } </h5>
            </Paper>
          </div>

          <canvas
            style={{
              backgroundColor: '#ffffff',
            }}
            id="usageChart"
            width="200"
            height="100"
          />

          <h5> Popular blocks </h5>
          <Table>
            <TableHeader
              displaySelectAll={false}
              adjustForCheckbox={false}
            >
              <TableRow>
                <TableHeaderColumn>Blocks</TableHeaderColumn>
                <TableHeaderColumn>Count</TableHeaderColumn>
              </TableRow>
            </TableHeader>
            <TableBody
              displayRowCheckbox={false}
            >
              {
                this.state.popularBlocks.map(b => (
                  <TableRow>
                    <TableRowColumn> { b[0] } </TableRowColumn>
                    <TableRowColumn> { b[1] } </TableRowColumn>
                  </TableRow>
                ))
              }
            </TableBody>
          </Table>

          <h5> Popular User Inputs </h5>
          <Table>
            <TableHeader
              displaySelectAll={false}
              adjustForCheckbox={false}
            >
              <TableRow>
                <TableHeaderColumn>Inputs</TableHeaderColumn>
                <TableHeaderColumn>Count</TableHeaderColumn>
              </TableRow>
            </TableHeader>
            <TableBody
              displayRowCheckbox={false}
            >
              {
                this.state.popularInputs.map(b => (
                  <TableRow>
                    <TableRowColumn> { b[0] } </TableRowColumn>
                    <TableRowColumn> { b[1] } </TableRowColumn>
                  </TableRow>
                ))
              }
            </TableBody>
          </Table>
        </div>
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
