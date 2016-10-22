import React from 'react'
import { hashHistory } from 'react-router'

import ActionGrade from 'material-ui/svg-icons/action/grade'
import ContentDrafts from 'material-ui/svg-icons/content/drafts'
import ContentInbox from 'material-ui/svg-icons/content/inbox'
import ContentSend from 'material-ui/svg-icons/content/send'
import Divider from 'material-ui/Divider'
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
    return (<Toolbar className="b-right-toolbar">
      <ToolbarGroup firstChild>
        <IconButton onTouchTap={this.handleToggle}>
          <NavigationMenu />
        </IconButton>
        <Drawer
          docked={false}
          width={200}
          open={this.state.leftMenuOpen}
          onRequestChange={leftMenuOpen => this.setState({ leftMenuOpen })}
        >
          <img className="b-logo" src={LogoPNG} alt="logo" />
          <Divider />
          <List>
            <ListItem onTouchTap={this.handleLink('/dashboard')} primaryText="Dashboard" leftIcon={<ContentSend />} />
            <ListItem onTouchTap={this.handleLink('/flow')} primaryText="Flow" leftIcon={<ContentInbox />} />
            <ListItem onTouchTap={this.handleLink('/broadcast')} primaryText="Broadcast" leftIcon={<ActionGrade />} />
            <ListItem onTouchTap={this.handleLink('/platforms')} primaryText="Platforms" leftIcon={<ContentDrafts />} />
            <ListItem onTouchTap={this.handleLink('/analytics')} primaryText="Analytics" leftIcon={<ContentInbox />} />
            <ListItem onTouchTap={this.handleLink('/help')} primaryText="Help" leftIcon={<ContentInbox />} />
          </List>
        </Drawer>
      </ToolbarGroup>
      <ConnectedRightToolbarGroup />
    </Toolbar>)
  }
}

export default TopBar
