import storage from 'store2'
import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Paper from 'material-ui/Paper'
import Subheader from 'material-ui/Subheader'

import { ACTIVE_BOT } from '../constants'
import * as platformActionCreators from '../actions/platformActionCreators'
import PlatformCard from '../components/Platform/PlatformCard'

class Platforms extends React.Component {
  constructor(props) {
    super(props)

    this.platformActions = bindActionCreators(
      platformActionCreators, this.props.dispatch)
  }

  componentWillMount() {
    this.platformActions.getPlatforms()
  }

  render() {
    const { platforms, platformIds, selectedBotId } = this.props

    return (<div>
      <Paper>
        {
          platformIds.filter(id =>
            !selectedBotId || platforms[id].botId === selectedBotId).map((id, index) => (
              <PlatformCard
                key={id}
                activeBotId={this.props.activeBotId}
                platform={platforms[id]}
                isFirst={index === 0}
                selectedBotId={selectedBotId}
              />
            ))
        }
      </Paper>
      {
        selectedBotId &&
        platformIds.filter(id => !platforms[id].botId).length > 0 && [
          <Subheader style={{ marginTop: '1.5em' }}>Quick add from existing platforms:</Subheader>,
          platformIds.filter(id => !platforms[id].botId).map((id, index) => (
            <PlatformCard
              key={id}
              activeBotId={this.props.activeBotId}
              platform={platforms[id]}
              isFirst={index === 0}
              selectedBotId={selectedBotId}
            />
          )),
        ]
      }
    </div>)
  }
}

Platforms.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  activeBotId: React.PropTypes.number,
  platformIds: React.PropTypes.arrayOf(React.PropTypes.number),
  platforms: React.PropTypes.objectOf(React.PropTypes.shape({})),
  selectedBotId: React.PropTypes.number,
}

const mapStateToProps = state => ({
  activeBotId: storage.get(ACTIVE_BOT) || -1,
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

const ConnectedPlatforms = connect(
  mapStateToProps,
)(Platforms)

export default ConnectedPlatforms
