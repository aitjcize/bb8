import React from 'react'
import { connect } from 'react-redux'

import Avatar from 'material-ui/Avatar'
import Chip from 'material-ui/Chip'
import Divider from 'material-ui/Divider'
import FlatButton from 'material-ui/FlatButton'
import IconContentLink from 'material-ui/svg-icons/content/link'
import { Menu, MenuItem } from 'material-ui/Menu'
import Popover from 'material-ui/Popover'
import Subheader from 'material-ui/Subheader'
import {
  Card,
  CardActions,
  CardHeader,
} from 'material-ui/Card'

import { FacebookIcon, LineIcon } from '../../assets/svgIcon'


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

export default ConnectedPlatformCard
