import React from 'react'
import { connect } from 'react-redux'

import { initializeApp } from '../actions'
import TopBar from '../components/TopBar'
import SideMenu from '../components/SideMenu'

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
  },
  topBar: {
    flex: 'none',
  },
  sideMenu: {
    width: '25vw',
    maxWidth: '15em',
    flex: 'none',
    zIndex: 9,
  },
  row: {
    flex: 1,
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
  },
  content: {
    overflow: 'scroll',
    height: '100%',
  },
}

class App extends React.Component {
  componentWillMount() {
    this.props.dispatchInit()
  }

  render() {
    return (<div style={styles.container}>
      <SideMenu style={styles.sideMenu} />
      <div style={styles.row}>
        <TopBar style={styles.topBar} />
        <div style={styles.content}>
          {this.props.children}
        </div>
      </div>
    </div>)
  }
}

App.propTypes = {
  dispatchInit: React.PropTypes.func,
  children: React.PropTypes.node,
}

const ConnectedApp = connect(
  () => ({}),
  dispatch => ({
    dispatchInit() {
      dispatch(initializeApp())
    },
  }),
)(App)

export default ConnectedApp
