import React from 'react'
import { connect } from 'react-redux'

import Paper from 'material-ui/Paper'

import TopBar from '../components/TopBar'
import SideMenu from '../components/SideMenu'
import Notification from '../components/Notification'

import { initializeApp } from '../actions/uiActionCreators'

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    boxShadow: 'none',
    borderRadius: 0,
    backgroundColor: 'transparent',
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
    overflow: 'hidden',
  },
  content: {
    overflow: 'scroll',
    height: '100%',
    position: 'relative',
  },
}

class App extends React.Component {
  componentWillMount() {
    this.props.dispatchInit()
  }

  render() {
    return (<Paper style={styles.container}>
      <Notification />
      { this.props.dialogComponent }
      <SideMenu style={styles.sideMenu} />
      <div style={styles.row}>
        <TopBar style={styles.topBar} />
        <div style={styles.content}>
          {this.props.children}
        </div>
      </div>
    </Paper>)
  }
}

App.propTypes = {
  dispatchInit: React.PropTypes.func,
  children: React.PropTypes.node,
  dialogComponent: React.PropTypes.element,
}

const ConnectedApp = connect(
  state => ({
    dialogComponent: state.dialog.component,
  }),
  dispatch => ({
    dispatchInit() {
      dispatch(initializeApp())
    },
  }),
)(App)

export default ConnectedApp
