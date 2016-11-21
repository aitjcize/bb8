import React from 'react'
import { connect } from 'react-redux'
import Dialog from 'material-ui/Dialog'
import Drawer from 'material-ui/Drawer'
import {
  Card,
  CardActions,
  CardHeader,
} from 'material-ui/Card'
import FlatButton from 'material-ui/FlatButton'
// import FloatingActionButton from 'material-ui/FloatingActionButton'
import Avatar from 'material-ui/Avatar'
import Paper from 'material-ui/Paper'
// import { List, ListItem } from 'material-ui/List'
import { Menu, MenuItem } from 'material-ui/Menu'
import Divider from 'material-ui/Divider'
import Chip from 'material-ui/Chip'
import Popover from 'material-ui/Popover'
import Subheader from 'material-ui/Subheader'

// import ContentAdd from 'material-ui/svg-icons/content/add'
import IconContentLink from 'material-ui/svg-icons/content/link'
import { FacebookIcon, LineIcon } from '../assets/svgIcon'

import { getPlatforms, updatePlatform, delPlatform } from '../actions/platformActionCreators'
import PlatformForm from '../components/PlatformForm'

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
  cardHeaderRightGroup: {
    flex: 1,
    display: 'flex',
    justifyContent: 'flex-end',
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

class PlatformCard extends React.Component {
  constructor(props) {
    super(props)

    this.handlePopoverOpen = this.handlePopoverOpen.bind(this)
    this.handleRequestClose = this.handleRequestClose.bind(this)

    this.state = {
      popoverOpen: false,
      popoverEl: undefined,
    }
  }

  handlePopoverOpen(e) {
    this.setState({
      popoverOpen: true,
      popoverEl: e.currentTarget,
    })
  }

  handleRequestClose() {
    this.setState({
      popoverOpen: false,
    })
  }

  render() {
    const { platform, bots, isFirst, selectedBotId } = this.props

      // console.log(platform)
      // console.log(platform.botId)

    const cardHeaderRightGroup = (
      <div
        style={styles.cardHeaderRightGroup}
      >
        {platform.botId ? <Chip
          onClick={this.handlePopoverOpen}
        >
          <Avatar>
            <IconContentLink />
          </Avatar>
          {
            bots[platform.botId] && bots[platform.botId].name
          }
        </Chip> : <FlatButton
          label="Assign a bot"
          labelPosition="before"
          onClick={this.handlePopoverOpen}
          icon={
            <IconContentLink />
          }
        />}
        <Popover
          open={this.state.popoverOpen}
          anchorEl={this.state.popoverEl}
          anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
          targetOrigin={{ horizontal: 'right', vertical: 'top' }}
          onRequestClose={this.handleRequestClose}
        >
          <Menu style={{ maxWidth: '25vw' }}>
            <Subheader>Assign a bot</Subheader>
            {Object.values(bots).map(b => (
              <MenuItem
                key={b.id}
                primaryText={b.name}
                style={{ fontSize: '.875em' }}
              />
            ))}
            {
              platform.botId && <div>
                <Divider />
                <MenuItem
                  primaryText="Detech"
                />
              </div>
            }
          </Menu>
        </Popover>
      </div>
    )

    return (<Card
      style={{
        backgroundColor: 'transparent',
        borderRadius: 0,
        boxShadow: 'none',
        transition: '.24s ease-out',
      }}
    >
      {!isFirst && <Divider /> }
      <CardHeader
        title={platform.name}
        subtitle={platform.botId ? 'Active' : 'Ready for assign'}
        avatar={platform.typeEnum === 'Facebook' ? <Avatar
          icon={<FacebookIcon />}
          backgroundColor="#0084FF"
        /> : <Avatar
          icon={<LineIcon />}
          backgroundColor="#00B900"
        />
        }
        style={{
          display: 'flex',
          alignItems: 'center',
        }}
      >
        {cardHeaderRightGroup}
      </CardHeader>
      {!selectedBotId && <CardActions>
        <FlatButton label="Edit" onTouchTap={this.props.handleEdit} />
        <FlatButton label="Delete" secondary onTouchTap={this.props.handleOpen} />
      </CardActions>}
    </Card>)
  }
}

PlatformCard.propTypes = {
  platform: React.PropTypes.shape({
    // name: React.PropTypes.string,
    // typeEnum: React.PropTypes.string,
  }),
  bots: React.PropTypes.shape({}),
  handleOpen: React.PropTypes.func,
  handleEdit: React.PropTypes.func,
  isFirst: React.PropTypes.bool,
  selectedBotId: React.PropTypes.number,
}

const mapPlatformCardStateToProps = state => ({
  bots: state.bots.ids.reduce((obj, id) =>
    Object.assign(obj, {
      [id]: state.entities.bots[id],
    }), {}),
})

const ConnectedPlatformCard = connect(
  mapPlatformCardStateToProps,
)(PlatformCard)

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
              <ConnectedPlatformCard
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
