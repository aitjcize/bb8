import React from 'react'
import { hashHistory } from 'react-router'

import stylePropType from 'react-style-proptype'
import ActionDashboard from 'material-ui/svg-icons/action/dashboard'
import { List, ListItem } from 'material-ui/List'
import Paper from 'material-ui/Paper'
import { Toolbar, ToolbarTitle } from 'material-ui/Toolbar'

import LogoImage from '../../assets/logo.svg'

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    borderRadius: 0,
  },
  logoContainer: {
    height: '20vw',
    maxHeight: '15em',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    margin: '1em 0',
  },
  logo: {
    width: '6em',
    height: '6em',
    opacity: 0.5,
    margin: '1em',
  },
  logoBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    backgroundColor: '#29D3A4',
  },
  copyrightText: {
    fontSize: '.7em',
  },
}

class SideMenu extends React.Component {

  constructor(props) {
    super(props)

    this.state = {}
  }

  render() {
    return (<Paper style={{ ...styles.container, ...this.props.style }}>
      <div>
        <Toolbar
          style={styles.logoBar}
        >
          <ToolbarTitle text="compose.ai" />
        </Toolbar>
        <List style={styles.list}>
          <ListItem
            onTouchTap={() => hashHistory.push('/botManager')}
            primaryText="Manage Chatbots"
            leftIcon={<ActionDashboard />}
          />
        </List>
      </div>
      <div style={styles.logoContainer}>
        <object type="image/svg+xml" data={LogoImage} style={styles.logo} />
        <div style={styles.copyrightText}>© 2016 compose.ai</div>
      </div>
    </Paper>)
  }
}

SideMenu.propTypes = {
  style: stylePropType,
}

export default SideMenu
