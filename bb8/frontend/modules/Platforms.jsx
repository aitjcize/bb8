import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

import Paper from 'material-ui/Paper'

import * as platformActionCreators from '../actions/platformActionCreators'
import PlatformCard from '../components/Platform/PlatformCard'

const styles = {
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
    return (
      <Paper>
        {
          this.props.platformIds.map((id, index) => {
            const plat = this.props.platforms[id]
            return (!this.props.selectedBotId || this.props.selectedBotId === plat.botId) && (
              <PlatformCard
                key={id}
                activeBotId={this.props.activeBotId}
                platform={plat}
                isFirst={index === 0}
                selectedBotId={this.props.selectedBotId}
              />)
          })
        }
        <div style={styles.floatButtonContainer} />
      </Paper>
    )
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

const ConnectedPlatforms = connect(
  mapStateToProps,
)(Platforms)

export default ConnectedPlatforms
