import React from 'react'
import { connect } from 'react-redux'

import Dialog from 'material-ui/Dialog'
import Drawer from 'material-ui/Drawer'
import FlatButton from 'material-ui/FlatButton'
import Paper from 'material-ui/Paper'

import { getPlatforms, updatePlatform, delPlatform } from '../actions/platformActionCreators'
import { PlatformCard, PlatformForm } from '../components/Platform'


const styles = {
  container: {

  },
  floatButtonContainer: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    padding: '1.25em',
    border: 'yellow 1px solid',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
}

const DeployStatus = (props) => {
  const { platform, activeBotId, dispatchAttachPlatform, dispatchDetachPlatform } = props
  const botId = platform.botId

  let statusComponent

  if (!botId) {
    statusComponent = (
      <FlatButton
        label="Attach"
        onClick={() => dispatchAttachPlatform(activeBotId, platform)}
      />)
  } else if (botId === activeBotId) {
    statusComponent = (
      <div>
        <span> Active </span>
        <FlatButton
          label="Detach"
          onClick={() => dispatchDetachPlatform(activeBotId, platform)}
        />
      </div>)
  } else {
    statusComponent = <span> Occupied </span>
  }

  return (
    <div> { statusComponent } </div>
  )
}

DeployStatus.propTypes = {
  dispatchAttachPlatform: React.PropTypes.func,
  dispatchDetachPlatform: React.PropTypes.func,
  activeBotId: React.PropTypes.number,
  platform: React.PropTypes.shape({}),
}

class Platforms extends React.Component {
  constructor(props) {
    super(props)

    this.handleOpenDialog = this.handleOpenDialog.bind(this)
    this.handleCloseDialog = this.handleCloseDialog.bind(this)
    this.handleOpenDrawer = this.handleOpenDrawer.bind(this)
    this.handleCloseDrawer = this.handleCloseDrawer.bind(this)
    this.handleDeletePlatform = this.handleDeletePlatform.bind(this)

    this.state = {
      dialogOpen: false,
      rightDrawerOpen: false,
      editingPlatform: { config: {} },
    }
  }

  componentWillMount() {
    this.props.getPlatforms()
  }

  handleOpenDialog(id) {
    this.setState({ dialogOpen: true, platformIdForDel: id })
  }

  handleCloseDialog() {
    this.setState({ dialogOpen: false })
  }

  handleDeletePlatform() {
    this.props.onDelPlatform(this.state.platformIdForDel)
    this.setState({ dialogOpen: false })
  }

  handleOpenDrawer(plat) {
    this.setState({ editingPlatform: plat, rightDrawerOpen: true })
  }

  handleCloseDrawer() {
    this.setState({ rightDrawerOpen: false })
  }

  render() {
    const actions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.handleCloseDialog}
      />,
      <FlatButton
        label="Delete"
        secondary
        keyboardFocused
        onTouchTap={this.handleDeletePlatform}
      />,
    ]

    return (
      <Paper
        style={styles.container}
      >
        {
          this.props.platformIds.map((id, index) => {
            const plat = this.props.platforms[id]
            return (!this.props.selectedBotId || this.props.selectedBotId === plat.botId) && (
              <PlatformCard
                key={id}
                activeBotId={this.props.activeBotId}
                dispatchAttachPlatform={this.props.dispatchAttachPlatform}
                dispatchDetachPlatform={this.props.dispatchDetachPlatform}
                handleEdit={() => this.handleOpenDrawer(plat)}
                handleOpen={() => this.handleOpenDialog(id)}
                platform={plat}
                isFirst={index === 0}
                selectedBotId={this.props.selectedBotId}
              />)
          })
        }

        <Dialog
          title="Confirm Delete"
          actions={actions}
          modal={false}
          open={this.state.dialogOpen}
          onRequestClose={this.handleCloseDialog}
        >
          Are you sure to delete?
        </Dialog>
        <Drawer
          docked={false}
          width={500}
          openSecondary
          open={this.state.rightDrawerOpen}
          onRequestChange={rightDrawerOpen => this.setState({ rightDrawerOpen })}
        >
          {
            this.state.rightDrawerOpen === false ? null :
            <PlatformForm
              handleClose={() =>
                this.setState({ rightDrawerOpen: false })}
              platform={this.state.editingPlatform}
            />
          }
        </Drawer>

        <div
          style={styles.floatButtonContainer}
        >
          {/*
          <FloatingActionButton
            onClick={() => this.handleOpenDrawer({ config: {} })}
            style={styles.floatButton}
            iconStyle={styles.floatButtonIcon}
          >
            <ContentAdd />
          </FloatingActionButton>
          */}
        </div>
      </Paper>
    )
  }
}

Platforms.propTypes = {
  activeBotId: React.PropTypes.number,
  dispatchAttachPlatform: React.PropTypes.func,
  dispatchDetachPlatform: React.PropTypes.func,
  platformIds: React.PropTypes.arrayOf(React.PropTypes.number),
  platforms: React.PropTypes.objectOf(React.PropTypes.shape({})),
  getPlatforms: React.PropTypes.func,
  onDelPlatform: React.PropTypes.func,
  selectedBotId: React.PropTypes.number,
}

const mapStateToProps = state => ({
  activeBotId: state.bots.active,
  platforms: state.platforms.ids.reduce((obj, id) =>
    Object.assign(obj, {
      [id]: state.entities.platforms[id],
    }), {}),
  platformIds: state.platforms.ids,
  bots: state.bots.ids.reduce((obj, id) =>
    Object.assign(obj, {
      [id]: state.entities.bots[id],
    }), {}),
})

const mapDispatchToProps = dispatch => ({
  dispatchAttachPlatform(botId, platform) {
    dispatch(updatePlatform(platform.id, { ...platform, botId }))
  },
  dispatchDetachPlatform(botId, platform) {
    dispatch(updatePlatform(platform.id, { ...platform, botId: null }))
  },
  getPlatforms() {
    dispatch(getPlatforms())
  },
  onDelPlatform(id) {
    dispatch(delPlatform(id))
  },
})

const ConnectedPlatforms = connect(
  mapStateToProps,
  mapDispatchToProps,
)(Platforms)

export default ConnectedPlatforms
