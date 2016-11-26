import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import Subheader from 'material-ui/Subheader'
import { List, ListItem } from 'material-ui/List'
import Paper from 'material-ui/Paper'
import FlatButton from 'material-ui/FlatButton'
import Divider from 'material-ui/Divider'
import Avatar from 'material-ui/Avatar'

import IconAdd from 'material-ui/svg-icons/content/add'

import Platforms from './Platforms'
import * as dialogActionCreators from '../actions/dialogActionCreators'

const styles = {
  container: {
    display: 'flex',
    flex: 1,
    padding: '1em',
    minHeight: '100%',
    boxSizing: 'border-box',
    alignItems: 'flex-start',
  },
  cols: {
    flex: 1,
    padding: '.5em',
    overflow: 'hidden',
    marginBottom: '10vh',
  },
  colsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
}

class BotManager extends React.Component {
  constructor(props) {
    super(props)

    this.handleBotSelect = this.handleBotSelect.bind(this)
    this.handleResetBotSelect = this.handleResetBotSelect.bind(this)

    this.dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    this.outerContainer = undefined

    this.state = {
      selectedBotId: undefined,
    }
  }

  handleBotSelect(id) {
    if (this.state.selectedBotId === id) return

    this.setState({
      selectedBotId: id,
    })
  }

  handleResetBotSelect(e) {
    if (e.target === this.outerContainer) {
      this.setState({
        selectedBotId: undefined,
      })
    }
  }

  render() {
    const { botIds, bots, platforms, platformIds } = this.props

    platformIds.map((id) => {
      const botId = platforms[id].botId
      if (!botId) return null

      if (!bots[botId].platforms) bots[botId].platforms = {}

      bots[botId].platforms[id] = platforms[id]

      return null
    })

    return (
      <div
        style={styles.container}
        ref={(c) => { this.outerContainer = c }}
        onClick={this.handleResetBotSelect}
      >
        <div style={styles.cols}>
          <Subheader
            style={styles.colsHeader}
          >
            My Chatbots
            <FlatButton
              label="New Chatbot"
              labelPosition="before"
              icon={<IconAdd />}
              onClick={this.dialogActions.openBotCreate}
            />
          </Subheader>

          <Paper>
            <List>
              { botIds.map((id, index) =>
                (<div
                  key={id}
                >
                  {index !== 0 && <Divider />}
                  <ListItem
                    primaryText={bots[id].name}
                    secondaryText={bots[id].description}
                    secondaryTextLines={2}
                    onClick={() => this.handleBotSelect(id)}
                    style={{
                      ...this.state.selectedBotId && this.state.selectedBotId !== id && {
                        opacity: 0.3,
                      },
                    }}
                    rightAvatar={
                      bots[id].platforms && <Avatar size={32}>
                        { Object.keys(bots[id].platforms).length }
                      </Avatar>
                    }
                  />
                </div>)
              )}
            </List>
          </Paper>
        </div>
        <div
          style={{
            ...styles.cols,
            ...{ flex: 2 },
          }}
        >
          <Subheader
            style={styles.colsHeader}
          >
            Platforms
            <FlatButton
              label="New Platform"
              labelPosition="before"
              icon={<IconAdd />}
            />
          </Subheader>
          <Platforms
            selectedBotId={this.state.selectedBotId}
          />
          {
            this.state.selectedBotId && (
              <div
                style={{
                  fontSize: '.8em',
                  margin: '1em 0',
                  padding: '0 1em',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                }}
              >
                <span>
                  {'Add new Platform and assign to Bot: '}
                  <b>{bots[this.state.selectedBotId].name}</b>
                </span>
                <FlatButton
                  label="New Platform"
                  style={{ margin: '.5em 0' }}
                  labelPosition="before"
                  icon={<IconAdd />}
                />
              </div>
            )
          }
        </div>
      </div>
    )
  }
}

BotManager.propTypes = {
  dispatch: React.PropTypes.func,
  botIds: React.PropTypes.arrayOf(React.PropTypes.number),
  bots: React.PropTypes.objectOf(React.PropTypes.shape({})),
  platformIds: React.PropTypes.arrayOf(React.PropTypes.number),
  platforms: React.PropTypes.objectOf(React.PropTypes.shape({})),
}

const mapStateToProps = state => ({
  bots: state.entities.bots,
  platforms: state.entities.platforms,
  botIds: state.bots.ids,
  platformIds: state.platforms.ids,
  activeId: state.bots.active,
})

const ConnectedBotManager = connect(
  mapStateToProps,
)(BotManager)

export default ConnectedBotManager
