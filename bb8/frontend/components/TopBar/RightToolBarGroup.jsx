import React from 'react'
import { connect } from 'react-redux'

import IconMoreVert from 'material-ui/svg-icons/navigation/more-vert'
import { ToolbarGroup } from 'material-ui/Toolbar'
import IconMenu from 'material-ui/IconMenu'
import FlatButton from 'material-ui/FlatButton'
import MenuItem from 'material-ui/MenuItem'

import { logout } from '../../actions/accountActionCreators'

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
  },
  menuItem: {
    minWidth: '8em',
  },
}

const RightToolbarGroup = props =>
  (<ToolbarGroup style={styles.container}>
    <IconMenu
      iconButtonElement={<FlatButton style={{ height: '100%' }} icon={<IconMoreVert color="white" />} />}
      anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      targetOrigin={{ horizontal: 'right', vertical: 'top' }}
      style={{ height: '100%', display: 'flex', alignItems: 'center' }}
    >
      <MenuItem
        onClick={() => props.dispatch(logout())}
        primaryText="Sign out"
        style={styles.menuItem}
      />
    </IconMenu>
  </ToolbarGroup>)

RightToolbarGroup.propTypes = {
  dispatch: React.PropTypes.func,
}

const ConnectedRightToolbarGroup = connect()(RightToolbarGroup)
export default ConnectedRightToolbarGroup
