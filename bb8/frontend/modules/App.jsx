import React from 'react'

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

const App = props => (
  <div style={styles.container}>
    <SideMenu style={styles.sideMenu} />
    <div style={styles.row}>
      <TopBar style={styles.topBar} />
      <div style={styles.content}>
        {props.children}
      </div>
    </div>
  </div>
)

App.propTypes = {
  children: React.PropTypes.node,
}

export default App
