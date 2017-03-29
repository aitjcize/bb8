import storage from 'store2'
import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { hashHistory } from 'react-router'

import Popover from 'material-ui/Popover'
import FlatButton from 'material-ui/FlatButton'
import { List, ListItem } from 'material-ui/List'
import Subheader from 'material-ui/Subheader'
import Divider from 'material-ui/Divider'

import IconArrowDropUp from 'material-ui/svg-icons/navigation/arrow-drop-up'
import IconArrowDropDown from 'material-ui/svg-icons/navigation/arrow-drop-down'

import { ACTIVE_BOT } from '../../constants'
import * as botActionCreators from '../../actions/botActionCreators'
import * as dialogActionCreators from '../../actions/dialogActionCreators'

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
    width: '25vw',
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

    this.botActions = bindActionCreators(
      botActionCreators, this.props.dispatch)
    this.dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    this.state = {
      open: false,
      createDialogOpen: false,
    }
  }

  handleTouchTap(event) {
    // This prevents ghost click.
    event.preventDefault()
    this.botActions.getAllBots()

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
    const { ids, activeId, data } = this.props
    const length = ids.length

    return (<FlatButton
      onTouchTap={this.handleTouchTap}
      label={data[activeId] ? this.props.data[activeId].name : 'Choose a bot'}
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
        onRequestClose={this.handleClosePicker}
      >
        <List
          style={styles.list}
        >
          {length === 0 ? null :
            (<div>
              <Subheader> Your Chatbots </Subheader>
              <div
                onMouseEnter={() => this.setState({ outerHover: true })}
                onMouseLeave={() => this.setState({ outerHover: false })}
              >
                { ids.map(id =>
                  (<BotListCell
                    key={id}
                    data={data[id]}
                    onSetActiveBot={this.botActions.setActiveBot}
                    handleClosePicker={this.handleClosePicker}
                    isActive={id === activeId}
                    outerHover={this.state.outerHover}
                  />)) }
              </div>
            </div>)
          }
        </List>
        <Divider />
        <List>
          <ListItem
            primaryText="Manage chatbots"
            style={styles.menuItem}
            onTouchTap={() => {
              hashHistory.push('/botManager')
              this.setState({
                open: false,
              })
            }}
          />
        </List>
      </Popover>
    </FlatButton>)
  }
}

BotPickerButton.propTypes = {
  dispatch: React.PropTypes.func,
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
  activeId: storage.get(ACTIVE_BOT) || -1,
})

const ConnectedBotPickerButton = connect(
  mapStateToProps,
)(BotPickerButton)

export default ConnectedBotPickerButton
