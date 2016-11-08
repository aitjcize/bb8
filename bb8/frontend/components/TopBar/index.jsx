import React from 'react'

import stylePropType from 'react-style-proptype'
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar'

import ConnectedBotPickerButton from './BotPickerButton'
import RightToolbarGroup from './RightToolBarGroup'

const styles = {
  container: {
    justifyContent: 'space-between',
  },
  buttonContainer: {
    alignItems: 'center',
  },
}

class TopBar extends React.Component {

  constructor(props) {
    super(props)

    this.state = {}
  }

  render() {
    return (<Toolbar style={{ ...styles.container, ...this.props.style }}>
      <ToolbarGroup firstChild style={styles.buttonContainer}>
        <ConnectedBotPickerButton />
      </ToolbarGroup>
      <RightToolbarGroup />
    </Toolbar>)
  }
}

TopBar.propTypes = {
  style: stylePropType,
}

export default TopBar
