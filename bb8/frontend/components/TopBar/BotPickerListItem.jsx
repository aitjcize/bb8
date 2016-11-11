import React from 'react'

import { ListItem } from 'material-ui/List'
import Avatar from 'material-ui/Avatar'
import IconCheck from 'material-ui/svg-icons/navigation/check'
// import { tealA700 } from 'material-ui/styles/colors'

import Theme from '../../constants/Theme'

const { palette } = Theme

const styles = {
  selected: {
    color: palette.accent1Color,
  },
}

class BotPickerListItem extends React.Component {

  constructor(props) {
    super(props)

    this.handleMouseEnter = this.handleMouseEnter.bind(this)
    this.handleMouseLeave = this.handleMouseLeave.bind(this)

    this.state = {
      selected: false,
      hover: false,
    }
  }

  handleMouseEnter() {
    this.setState({
      hover: true,
    })
  }

  handleMouseLeave() {
    this.setState({
      hover: false,
    })
  }

  // TODO: Seleted, active and hover styles

  render() {
    const {
      onSetActiveBot,
      handleClosePicker,
      isActive,
      data } = this.props
    const { name, description, id } = data
    const { hover } = this.state

    return (<ListItem
      primaryText={name}
      secondaryText={description}
      onTouchTap={() => {
        handleClosePicker()
        onSetActiveBot(id)
      }}
      onMouseEnter={this.handleMouseEnter}
      onMouseLeave={this.handleMouseLeave}
      leftAvatar={
        <Avatar>
          {name.slice(0, 2).toUpperCase()}
        </Avatar>
      }
      rightIcon={(hover || isActive) ? <IconCheck /> : null}
      style={isActive && styles.selected}
    />)
  }
}

BotPickerListItem.propTypes = {
  onSetActiveBot: React.PropTypes.func,
  handleClosePicker: React.PropTypes.func,
  data: React.PropTypes.shape({
    // eslint-disable-next-line react/no-unused-prop-types
    id: React.PropTypes.number,
    // eslint-disable-next-line react/no-unused-prop-types
    name: React.PropTypes.string,
    // eslint-disable-next-line react/no-unused-prop-types
    description: React.PropTypes.string,
  }),
  isActive: React.PropTypes.bool,
}

export default BotPickerListItem
