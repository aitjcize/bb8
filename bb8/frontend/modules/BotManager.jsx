import storage from 'store2'
import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import Subheader from 'material-ui/Subheader'
import { List, ListItem } from 'material-ui/List'
import Paper from 'material-ui/Paper'
import Chip from 'material-ui/Chip'
import FlatButton from 'material-ui/FlatButton'
import Divider from 'material-ui/Divider'
import IconButton from 'material-ui/IconButton'

import IconAdd from 'material-ui/svg-icons/content/add'
import IconShortText from 'material-ui/svg-icons/editor/short-text'

import Platforms from './Platforms'
import { ACTIVE_BOT } from '../constants'
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
    marginBottom: '10vh',
    minWidth: 300,
  },
  colsHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  hintText: {
    textAlign: 'center',
    margin: '1.5em 0',
  },
  hintTextLink: {
    color: '#757575',
    padding: '.5em',
    textDecoration: 'underline',
    cursor: 'pointer',
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
    const { selectedBotId } = this.state

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
          </Subheader>
          <Paper>
            {
              <List
                style={{
                  ...Object.keys(botIds).length === 1 || selectedBotId ? { padding: 0 } : {},
                }}
              >
                { botIds.map((id, index) =>
                !(selectedBotId && selectedBotId !== id) && [
                  !selectedBotId && index !== 0 && <Divider />,
                  <ListItem
                    key={id}
                    primaryText={
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ wordBreak: 'break-all' }}>
                          {bots[id].name}
                        </span>
                        <span style={{ marginLeft: '1em', marginTop: '-.5em' }}>
                          {
                            selectedBotId ?
                            bots[id].gaId && (<Chip>{`gaId: #${bots[id].gaId}`}</Chip>) :
                            (platformIds.filter(v => platforms[v].botId === id).length > 0)
                            && <IconShortText />
                          }
                        </span>
                      </div>
                    }
                    secondaryText={
                      <span
                        style={{
                          width: '100%',
                          height: 'auto',
                          maxHeight: '2.2em',
                          whiteSpace: 'pre-wrap',
                          overflow: 'hidden',
                          display: 'inline-block',
                        }}
                      >
                        {bots[id].description}
                      </span>
                    }
                    onClick={() => this.handleBotSelect(id)}
                    disabled={!!selectedBotId}
                    innerDivStyle={{
                      ...selectedBotId && selectedBotId !== id ? {
                        opacity: 0.3,
                      } : {},
                    }}
                  />,
                  selectedBotId === id && <div style={{ padding: '.5em' }}>
                    <FlatButton
                      label="edit"
                      onClick={() =>
                        this.dialogActions.openBotUpdate(
                          id, bots[id].name, bots[id].description, bots[id].gaId)}
                    />
                    <FlatButton
                      label="delete"
                      onClick={() => this.dialogActions.openBotDelete(id)}
                    />
                  </div>,
                ]
              )}
              </List>
            }
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
            {
              selectedBotId ? <span>
                {'Platforms for '}
                <b style={{ color: '#757575' }}>
                  {selectedBotId && bots[selectedBotId].name}
                </b>
              </span> : 'All Platforms'
            }

            <IconButton
              onClick={() => this.dialogActions.openCreatePlatform()}
              tooltip="Add platform"
              tooltipPosition="bottom-center"
            >
              <IconAdd />
            </IconButton>
          </Subheader>
          {
            platformIds.length === 0 ? <Subheader style={styles.hintText}>
              {'You don\'t have any platforms.'}
              <b
                style={styles.hintTextLink}
                onClick={() => this.dialogActions.openCreatePlatform()}
              >
                Create new
              </b>
              !
            </Subheader> :
            selectedBotId &&
            Object.keys(platforms).filter(v =>
              platforms[v].botId === selectedBotId).length === 0 &&
              <Subheader style={styles.hintText}>
                {`There are no platforms assigned to ${bots[selectedBotId].name}.`}
              </Subheader>
          }
          <Platforms
            selectedBotId={selectedBotId}
          />
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
  activeId: storage.get(ACTIVE_BOT) || -1,
})

const ConnectedBotManager = connect(
  mapStateToProps,
)(BotManager)

export default ConnectedBotManager
