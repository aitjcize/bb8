import React from 'react'
import { connect } from 'react-redux'
import Popover from 'material-ui/Popover'
import Menu from 'material-ui/Menu'
import RaisedButton from 'material-ui/RaisedButton'
import ImmutablePropTypes from 'react-immutable-proptypes'
import ContentAdd from 'material-ui/svg-icons/content/add'
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar'
import NavigationExpandMoreIcon from 'material-ui/svg-icons/navigation/expand-more'
import MenuItem from 'material-ui/MenuItem'
import IconMenu from 'material-ui/IconMenu'
import IconButton from 'material-ui/IconButton'

import LogoPNG from '../assets/logo.png'
import actions from '../actions'

class RightToolbarGroup extends React.Component {

  constructor(props) {
    super(props)

    this.handleTouchTap = this.handleTouchTap.bind(this)
    this.handleRequestClose = this.handleRequestClose.bind(this)
    this.state = {
      open: false,
    }
  }

  handleTouchTap(event) {
    // This prevents ghost click.
    event.preventDefault()

    const { data } = this.props

    if (data && data.size) {
      this.setState({
        open: true,
        anchorEl: event.currentTarget,
      })
    }
    // else {
    //   TODO: open create bot dialog
    // }
  }

  handleRequestClose() {
    this.setState({
      open: false,
    })
  }

  render() {
    const { data, activeId, onSetActiveBot } = this.props
    const length = data.get('result').size
    return (
      <ToolbarGroup>
        <RaisedButton
          primary
          onTouchTap={this.handleTouchTap}
          label={activeId === -1 ? 'Add a bot' : data.get('entities').get('bots').get(activeId).get('name')}
        />
        <Popover
          open={this.state.open}
          anchorEl={this.state.anchorEl}
          anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
          targetOrigin={{ horizontal: 'left', vertical: 'top' }}
          onRequestClose={this.handleRequestClose}
        >
          <Menu>
            {length === 0 ? null :
             data.get('result')
               .map(id =>
                 (<MenuItem
                   key={id}
                   primaryText={data.get('entities').get('bots').get(id).get('name')}
                   onTouchTap={() => onSetActiveBot(id)}
                 />))
            }
            <MenuItem primaryText="Add a bot" leftIcon={<ContentAdd />} />
          </Menu>
        </Popover>
        <IconMenu
          iconButtonElement={
            <IconButton touch>
              <NavigationExpandMoreIcon />
            </IconButton>
          }
        >
          <MenuItem primaryText="My Account" />
        </IconMenu>
      </ToolbarGroup>)
  }
}

RightToolbarGroup.propTypes = {
  onSetActiveBot: React.PropTypes.func,
  data: ImmutablePropTypes.map,
  activeId: React.PropTypes.number,
}

const mapStateToProps = state => ({
  data: state.get('bots').get('listing'),
  activeId: state.get('bots').get('active'),
})

const mapDispatchToProps = dispatch => ({
  onSetActiveBot(id) {
    dispatch(actions.setActiveBot(id))
  },
})

const ConnectedRightToolbarGroup = connect(
  mapStateToProps,
  mapDispatchToProps,
)(RightToolbarGroup)

const TopBar = () => (
  <Toolbar className="b-right-toolbar">
    <ToolbarGroup firstChild>
      <img className="b-logo" src={LogoPNG} alt="logo" />
    </ToolbarGroup>
    <ConnectedRightToolbarGroup />
  </Toolbar>
)

export default TopBar
