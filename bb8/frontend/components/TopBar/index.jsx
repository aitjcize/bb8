import React from 'react'
import { hashHistory } from 'react-router'

import ActionDashboard from 'material-ui/svg-icons/action/dashboard'
import ActionTimeline from 'material-ui/svg-icons/action/timeline'
import ActionHelp from 'material-ui/svg-icons/action/help'
import CommunicationChatBubbleOutline from 'material-ui/svg-icons/communication/chat-bubble-outline'
import ImageLooks from 'material-ui/svg-icons/image/looks'
import HardwareDeviceHub from 'material-ui/svg-icons/hardware/device-hub'
import Drawer from 'material-ui/Drawer'
import IconButton from 'material-ui/IconButton'
import NavigationMenu from 'material-ui/svg-icons/navigation/menu'
import { List, ListItem } from 'material-ui/List'
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar'

import ConnectedRightToolbarGroup from './RightToolBarGroup'
import LogoPNG from '../../assets/logo.png'

class TopBar extends React.Component {

  constructor(props) {
    super(props)

    this.handleClose = this.handleClose.bind(this)
    this.handleToggle = this.handleToggle.bind(this)
    this.handleClose = this.handleClose.bind(this)
    this.state = {
      leftMenuOpen: false,
    }
  }

  handleLink(path) {
    return () => {
      this.handleToggle()
      hashHistory.push(path)
    }
  }

  handleToggle() {
    this.setState({ leftMenuOpen: !this.state.leftMenuOpen })
  }

  handleClose() {
    this.setState({ leftMenuOpen: false })
  }

  render() {
    return (<Toolbar className="b-toolbar">
      <ToolbarGroup firstChild>
        <IconButton
          onTouchTap={this.handleToggle}
          style={{ width: '56px', height: '56px' }}
          iconStyle={{ color: 'white' }}
        >
          <NavigationMenu />
        </IconButton>
        <Drawer
          docked={false}
          width={320}
          open={this.state.leftMenuOpen}
          onRequestChange={leftMenuOpen => this.setState({ leftMenuOpen })}
        >
          <img className="b-logo" src={LogoPNG} alt="logo" />
          <List>
            <ListItem
              onTouchTap={this.handleLink('/dashboard')}
              primaryText="Dashboard"
              leftIcon={<ActionDashboard />}
            />
            <ListItem
              onTouchTap={this.handleLink('/flow')}
              primaryText="Flow"
              leftIcon={<HardwareDeviceHub />}
            />
            <ListItem
              onTouchTap={this.handleLink('/broadcast')}
              primaryText="Broadcast"
              leftIcon={<ImageLooks />}
            />
            <ListItem
              onTouchTap={this.handleLink('/platforms')}
              primaryText="Platforms"
              leftIcon={<CommunicationChatBubbleOutline />}
            />
            <ListItem
              onTouchTap={this.handleLink('/analytics')}
              primaryText="Analytics"
              leftIcon={<ActionTimeline />}
            />
            <ListItem
              onTouchTap={this.handleLink('/help')}
              primaryText="Help"
              leftIcon={<ActionHelp />}
            />
          </List>
        </Drawer>
      </ToolbarGroup>
      <ConnectedRightToolbarGroup />
    </Toolbar>)
  }
}

export default TopBar
