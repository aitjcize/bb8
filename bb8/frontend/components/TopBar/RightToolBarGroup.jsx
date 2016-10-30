import React from 'react'
import { connect } from 'react-redux'

import ContentAdd from 'material-ui/svg-icons/content/add'
import IconButton from 'material-ui/IconButton'
import IconMenu from 'material-ui/IconMenu'
import Menu from 'material-ui/Menu'
import MenuItem from 'material-ui/MenuItem'
import NavigationExpandMoreIcon from 'material-ui/svg-icons/navigation/expand-more'
import Popover from 'material-ui/Popover'
import RaisedButton from 'material-ui/RaisedButton'
import { ToolbarGroup } from 'material-ui/Toolbar'

import { setActiveBot } from '../../actions'

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

    if (this.props.ids.length) {
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
    const { ids, activeId, onSetActiveBot } = this.props
    const length = ids.length
    return (
      <ToolbarGroup>
        <RaisedButton
          primary
          onTouchTap={this.handleTouchTap}
          label={activeId === -1 ? 'Add a bot' : this.props.data[activeId].name}
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
               ids.map(id =>
                 (<MenuItem
                   key={id}
                   primaryText={this.props.data[id].name}
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
  ids: React.PropTypes.arrayOf(React.PropTypes.number),
  data: React.PropTypes.objectOf(React.PropTypes.shape({
    name: React.PropTypes.string,
  })),
  activeId: React.PropTypes.number,
}

const mapStateToProps = state => ({
  data: state.bots.ids.reduce((obj, id) =>
    Object.assign(obj, {
      [id]: state.entities.bots[id],
    }), {}),
  ids: state.bots.ids,
  activeId: state.bots.active,
})

const mapDispatchToProps = dispatch => ({
  onSetActiveBot(id) {
    dispatch(setActiveBot(id))
  },
})

const ConnectedRightToolbarGroup = connect(
  mapStateToProps,
  mapDispatchToProps,
)(RightToolbarGroup)

export default ConnectedRightToolbarGroup
