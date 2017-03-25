import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import Avatar from 'material-ui/Avatar'
import Chip from 'material-ui/Chip'
import Paper from 'material-ui/Paper'
import Divider from 'material-ui/Divider'
import FlatButton from 'material-ui/FlatButton'
import IconSwapHoriz from 'material-ui/svg-icons/action/swap-horiz'
import { Menu, MenuItem } from 'material-ui/Menu'
import Popover from 'material-ui/Popover'
import Subheader from 'material-ui/Subheader'
import {
  Card,
  CardActions,
  CardHeader,
} from 'material-ui/Card'

import FbMessengerIcon from '../../assets/svgIcon/FbMessengerIcon'
import LineIcon from '../../assets/svgIcon/LineIcon'
import * as dialogActionCreators from '../../actions/dialogActionCreators'
import * as platformActionCreators from '../../actions/platformActionCreators'

const styles = {
  cardHeaderRightGroup: {
    flex: 1,
    display: 'flex',
    justifyContent: 'flex-end',
  },
}

class PlatformCard extends React.Component {
  constructor(props) {
    super(props)

    this.handlePopoverOpen = this.handlePopoverOpen.bind(this)
    this.handleRequestClose = this.handleRequestClose.bind(this)

    this.dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)
    this.platformActions = bindActionCreators(
      platformActionCreators, this.props.dispatch)

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

    const cardHeaderRightGroup = (
      <div style={styles.cardHeaderRightGroup}>
        {platform.botId ? <Paper
          zDepth={this.state.dropdownHover ? 0 : 1}
          style={{ overflow: 'hidden', borderRadius: '10em' }}
        >
          <Chip
            onClick={this.handlePopoverOpen}
            style={{
              ...{
                minWidth: '5em',
                transition: '.24s ease-out',
                cursor: 'pointer',
              },
              ...this.state.dropdownHover ? { opacity: 0.5 } : {},
            }}
            onMouseEnter={() => this.setState({ dropdownHover: true })}
            onMouseLeave={() => this.setState({ dropdownHover: false })}
          >
            <Avatar>
              <IconSwapHoriz />
            </Avatar>
            {
              bots[platform.botId] && bots[platform.botId].name
            }
          </Chip>
        </Paper> : <FlatButton
          label="Assign"
          labelPosition="before"
          onClick={this.handlePopoverOpen}
          icon={
            <IconSwapHoriz />
          }
          style={{ textTransform: 'capitalize' }}
        />}
        <Popover
          open={this.state.popoverOpen}
          anchorEl={this.state.popoverEl}
          anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
          targetOrigin={{ horizontal: 'right', vertical: 'top' }}
          onRequestClose={this.handleRequestClose}
        >
          <Menu style={{ maxWidth: '25vw', minWidth: '10vw' }}>
            <Subheader>Choose a bot</Subheader>
            {Object.values(bots).map(b => (
              <MenuItem
                key={b.id}
                primaryText={b.name}
                onTouchTap={
                  () => {
                    this.platformActions.updatePlatform(
                      platform.id, { ...platform, botId: b.id })
                    this.setState({ popoverOpen: false })
                  }
                }
                style={{ fontSize: '.875em' }}
              />
            ))}
            {
              platform.botId && <div>
                <Divider />
                <MenuItem
                  primaryText="Detach"
                  onTouchTap={
                    () => {
                      this.platformActions.updatePlatform(
                        platform.id, { ...platform, botId: null })
                      this.setState({ popoverOpen: false })
                    }
                  }
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
          icon={<FbMessengerIcon />}
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
        <FlatButton
          label="Edit"
          onTouchTap={() =>
            this.dialogActions.openUpdatePlatform(this.props.platform)}
        />
        <FlatButton
          label="Delete"
          secondary
          onTouchTap={() =>
            this.dialogActions.openDelPlatform(this.props.platform)}
        />
      </CardActions>}
    </Card>)
  }
}

PlatformCard.propTypes = {
  dispatch: React.PropTypes.func,
  platform: React.PropTypes.shape({}).isRequired,
  bots: React.PropTypes.shape({}),
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

export default ConnectedPlatformCard
