import React from 'react'
import { connect } from 'react-redux'
import Dialog from 'material-ui/Dialog'
import Drawer from 'material-ui/Drawer'
import { Card, CardActions } from 'material-ui/Card'
import FlatButton from 'material-ui/FlatButton'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import ContentAdd from 'material-ui/svg-icons/content/add'

import LineLogo from '../assets/line_logo.png'
import FBLogo from '../assets/facebook_logo.png'

import { getPlatforms, delPlatform } from '../actions'
import PlatformForm from '../components/PlatformForm'

const DeployStatus = (props) => {
  const { platform, activeBotId } = props
  const botId = platform.botId

  let statusComponent

  if (!botId) {
    statusComponent = <FlatButton label="Attach" />
  } else if (botId === activeBotId) {
    statusComponent = <span className="b-platform-card__status--active"> Active </span>
  } else {
    statusComponent = <span className="b-platform-card__status--occupied"> Occupied </span>
  }

  return (
    <div> { statusComponent } </div>
  )
}

DeployStatus.propTypes = {
  activeBotId: React.PropTypes.number,
  platform: React.PropTypes.shape({}),
}

const PlatformCard = props => (
  <Card className="b-platform-card">
    <div className="b-platform-card__body">
      <img
        className="b-platform-card__logo"
        src={props.platform.typeEnum === 'Facebook' ?
             FBLogo : LineLogo}
        alt="facebook logo"
      />
      <div className="b-platform-card__info">
        <span className="b-platform-card__name">
          {props.platform.name}
        </span>
      </div>
      <DeployStatus {...props} />
    </div>
    <CardActions>
      <FlatButton label="Edit" onTouchTap={props.handleEdit} />
      <FlatButton label="Delete" secondary onTouchTap={props.handleOpen} />
    </CardActions>
  </Card>
)

PlatformCard.propTypes = {
  platform: React.PropTypes.shape({
    name: React.PropTypes.string,
    typeEnum: React.PropTypes.string,
  }),
  handleOpen: React.PropTypes.func,
  handleEdit: React.PropTypes.func,
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
      <div>
        {
          this.props.platformIds.map((id) => {
            const plat = this.props.platforms[id]
            return (
              <PlatformCard
                key={id}
                handleEdit={() => this.handleOpenDrawer(plat)}
                handleOpen={() => this.handleOpenDialog(id)}
                platform={plat}
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
          { this.state.rightDrawerOpen === false ? null :
            <PlatformForm
              handleClose={() => this.setState({ rightDrawerOpen: false })}
              platform={this.state.editingPlatform}
            /> }
        </Drawer>

        <FloatingActionButton
          onClick={() => this.handleOpenDrawer({ config: {} })}
          className="b-add-platform-btn"
        >
          <ContentAdd />
        </FloatingActionButton>
      </div>
    )
  }
}

Platforms.propTypes = {
  platformIds: React.PropTypes.arrayOf(React.PropTypes.number),
  platforms: React.PropTypes.objectOf(React.PropTypes.shape({})),
  getPlatforms: React.PropTypes.func,
  onDelPlatform: React.PropTypes.func,
}

const mapStateToProps = state => ({
  activeBotId: state.bots.active,
  platforms: state.platforms.ids.reduce((obj, id) =>
    Object.assign(obj, {
      [id]: state.entities.platforms[id],
    }), {}),
  platformIds: state.platforms.ids,
})

const mapDispatchToProps = dispatch => ({
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
