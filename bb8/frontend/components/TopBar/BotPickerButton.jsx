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

import { setActiveBot, getAllBots } from '../../actions'

import BotListCell from './BotPickerListItem'
import BotCreateDialog from './BotCreateDialog'

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
    this.handleClosePicker = this.handleClosePicker.bind(this)
    this.state = {
      open: false,
      createDialogOpen: false,
    }
  }

  handleTouchTap(event) {
    // This prevents ghost click.
    event.preventDefault()

    this.props.dispatchGetAllBots()

    this.setState({
      open: true,
      anchorEl: event.currentTarget,
    })
  }

  handleClosePicker() {
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
      <BotCreateDialog
        open={this.state.createDialogOpen}
        handleClose={() => this.setState({ createDialogOpen: false })}
      />
      <Popover
        open={this.state.open}
        anchorEl={this.state.anchorEl}
        anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
        targetOrigin={{ horizontal: 'left', vertical: 'top' }}
        onRequestClose={this.handleClosePicker}
      >
        <Menu>
          <MenuItem
            primaryText="Create a bot"
            style={styles.menuItem}
            onClick={() => this.setState({
              open: false,
              createDialogOpen: true,
            })}
          />
        </Menu>
        <Divider />
        <List
          style={styles.list}
        >
          {length === 0 ? null :
            (<div>
              <Subheader> Your Chatbots </Subheader>
              { ids.map(id =>
                (<BotListCell
                  key={id}
                  data={data[id]}
                  onSetActiveBot={onSetActiveBot}
                  handleClosePicker={this.handleClosePicker}
                  isActive={id === activeId}
                />)) }
              <Divider />
            </div>)
          }
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
  dispatchGetAllBots: React.PropTypes.func,
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
  dispatchGetAllBots() {
    dispatch(getAllBots())
  },
})

const ConnectedBotPickerButton = connect(
  mapStateToProps,
  mapDispatchToProps,
)(BotPickerButton)

export default ConnectedBotPickerButton
