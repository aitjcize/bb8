import React from 'react'
import { connect } from 'react-redux'

import IconMoreVert from 'material-ui/svg-icons/navigation/more-vert'
import { ToolbarGroup } from 'material-ui/Toolbar'
import IconMenu from 'material-ui/IconMenu'
import IconButton from 'material-ui/IconButton'
import MenuItem from 'material-ui/MenuItem'

import { logout } from '../../actions/accountActionCreators'

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

const RightToolbarGroup = props =>
  (<ToolbarGroup style={styles.container}>
    <IconMenu
      iconButtonElement={<IconButton> <IconMoreVert /> </IconButton>}
      anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
      targetOrigin={{ horizontal: 'right', vertical: 'top' }}
    >
      <MenuItem
        onClick={() => props.dispatch(logout())}
        primaryText="Sign out"
      />
    </IconMenu>
  </ToolbarGroup>)

RightToolbarGroup.propTypes = {
  dispatch: React.PropTypes.func,
}

const ConnectedRightToolbarGroup = connect()(RightToolbarGroup)
export default ConnectedRightToolbarGroup
