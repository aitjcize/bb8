import React from 'react'
import { connect } from 'react-redux'

import Popover from 'material-ui/Popover'
import FlatButton from 'material-ui/FlatButton'
import { List } from 'material-ui/List'
import Subheader from 'material-ui/Subheader'
import Divider from 'material-ui/Divider'
import Menu from 'material-ui/Menu'
import MenuItem from 'material-ui/MenuItem'

import IconArrowDropUp from 'material-ui/svg-icons/navigation/arrow-drop-up'
import IconArrowDropDown from 'material-ui/svg-icons/navigation/arrow-drop-down'

import { setActiveBot } from '../../actions'

import BotListCell from './BotPickerListItem'

const styles = {
  button: {
    color: 'white',
    height: '100%',
    position: 'relative',
  },
  buttonText: {
    margin: '0 1.5em',
  },
  list: {
    width: '100%',
    minWidth: '15em',
  },
  menuItem: {
    fontSize: '.875em',
  },
}

class BotPickerButton extends React.Component {

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
    const { ids, activeId, onSetActiveBot, data } = this.props
    const length = ids.length

    return (<FlatButton
      onTouchTap={this.handleTouchTap}
      label={activeId === -1 ? 'Choose a bot' : this.props.data[activeId].name}
      labelPosition="before"
      icon={this.state.open ? <IconArrowDropUp /> : <IconArrowDropDown />}
      labelStyle={styles.buttonText}
      style={styles.button}
    >
      <Popover
        open={this.state.open}
        anchorEl={this.state.anchorEl}
        anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
        targetOrigin={{ horizontal: 'left', vertical: 'top' }}
        onRequestClose={this.handleRequestClose}
      >
        <List
          style={styles.list}
        >
          <Subheader>testtitle</Subheader>
          {length === 0 ? null :
            ids.map(id =>
              (<BotListCell
                key={id}
                data={data[id]}
                onSetActiveBot={onSetActiveBot}
                isActive={id === activeId}
              />))
          }
          <Divider />
          <Menu>
            <MenuItem
              primaryText="Manage BOTS"
              style={styles.menuItem}
            />
          </Menu>
        </List>
      </Popover>
    </FlatButton>)
  }
}

BotPickerButton.propTypes = {
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

const ConnectedBotPickerButton = connect(
  mapStateToProps,
  mapDispatchToProps,
)(BotPickerButton)

export default ConnectedBotPickerButton
