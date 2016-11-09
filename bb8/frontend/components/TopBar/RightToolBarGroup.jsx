import React from 'react'

import IconMoreVert from 'material-ui/svg-icons/navigation/more-vert'
import { ToolbarGroup } from 'material-ui/Toolbar'
import FlatButton from 'material-ui/FlatButton'

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
  },
  button: {
    height: '100%',
    color: 'white',
  },
}

class RightToolbarGroup extends React.Component {

  constructor(props) {
    super(props)


    // TODO: popover
    this.state = {
      open: false,
    }
  }

  render() {
    return (
      <ToolbarGroup style={styles.container}>
        <FlatButton
          icon={<IconMoreVert />}
          style={styles.button}
        />
      </ToolbarGroup>)
  }
}

RightToolbarGroup.propTypes = {
}

export default RightToolbarGroup
