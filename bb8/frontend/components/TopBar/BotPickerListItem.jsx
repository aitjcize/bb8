import React from 'react'

import { ListItem } from 'material-ui/List'
import Avatar from 'material-ui/Avatar'
import IconCheck from 'material-ui/svg-icons/navigation/check'

const styles = {
  selected: {
    color: 'red',
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
    const { onSetActiveBot, isActive, data } = this.props
    const { name, description, id } = data
    const { hover } = this.state

    return (<ListItem
      primaryText={name}
      secondaryText={description}
      onTouchTap={() => onSetActiveBot(id)}
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
  data: React.PropTypes.objectOf(React.PropTypes.shape({
    // eslint-disable-next-line react/no-unused-prop-types
    name: React.PropTypes.string,
  })),
  isActive: React.PropTypes.bool,
}

export default BotPickerListItem
