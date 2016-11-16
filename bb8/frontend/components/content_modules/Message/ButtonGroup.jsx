import React from 'react'

import FlatButton from 'material-ui/FlatButton'

const styles = {
  container: {
    margin: '.5em 0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  children: {
  },
}

const ButtonGroup = (props) => {
  const deleteButton = (
    <FlatButton
      label="remove"
      onClick={props.onRemoveClicked}
    />
  )

  return (
    <div style={styles.container}>
      {props.onRemoveClicked && deleteButton}
      {props.children}
    </div>
  )
}

ButtonGroup.propTypes = {
  children: React.PropTypes.node,
  onRemoveClicked: React.PropTypes.func,
}

export default ButtonGroup
