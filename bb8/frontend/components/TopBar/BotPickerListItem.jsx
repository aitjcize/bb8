import React from 'react'

import { ListItem } from 'material-ui/List'
import Avatar from 'material-ui/Avatar'
import IconCheck from 'material-ui/svg-icons/navigation/check'

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

    this.state = {
      selected: false,
      hover: false,
    }
  }

  // TODO: Seleted, active and hover styles

  render() {
    const {
      onSetActiveBot,
      handleClosePicker,
      isActive,
      data } = this.props
    const { name, description, id } = data


    return (<ListItem
      primaryText={name}
      secondaryText={
        <span
          style={{ ...isActive && styles.selected }}
        >
          {description}
        </span>
      }
      secondaryTextLines={2}
      onTouchTap={() => {
        handleClosePicker()
        onSetActiveBot(id)
      }}
      onMouseEnter={() => this.setState({ hover: true })}
      onMouseLeave={() => this.setState({ hover: false })}
      leftAvatar={
        <Avatar>
          {name.slice(0, 2).toUpperCase()}
        </Avatar>
      }
      rightIcon={((this.props.outerHover && this.state.hover) ||
        (!this.props.outerHover && isActive)) ? <IconCheck /> : null}
      style={isActive ? styles.selected : {}}
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
  outerHover: React.PropTypes.bool,
}

export default BotPickerListItem
