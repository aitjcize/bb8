import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'

import orderBy from 'lodash/orderBy'
import ContentAdd from 'material-ui/svg-icons/content/add'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import Subheader from 'material-ui/Subheader'

import { BroadcastItem, BroadcastEditor } from '../components/Broadcast'
import * as broadcastActionCreators from '../actions/broadcastActionCreators'
import * as dialogActionCreators from '../actions/dialogActionCreators'
import * as uiActionCreators from '../actions/uiActionCreators'

const styles = {
  container: {
    padding: '1em',
  },
  floatButton: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    margin: '1.5em',
  },
}

class Broadcast extends React.Component {
  constructor(props) {
    super(props)

    this.handleOpenEditor = this.handleOpenEditor.bind(this)
    this.handleCloseEditor = this.handleCloseEditor.bind(this)
    this.renderBroadcastEditor = this.renderBroadcastEditor.bind(this)
    this.handleKeyDownEsc = this.handleKeyDownEsc.bind(this)

    this.broadcastActions = bindActionCreators(
      broadcastActionCreators, this.props.dispatch)
    this.uiActions = bindActionCreators(
      uiActionCreators, this.props.dispatch)

    this.state = {
      editorOpen: false,
      creating: false,
      editingBroadcast: { },
    }
  }


  componentWillMount() {
    const broadcastActions = bindActionCreators(
      broadcastActionCreators, this.props.dispatch)
    broadcastActions.getAllBroadcasts(this.props.activeBotId)
  }

  componentDidMount() {
    window.addEventListener('keydown', this.handleKeyDownEsc)
  }

  componentWillUnmount() {
    window.removeEventListener('keydown', this.handleKeyDownEsc)
  }

  handleOpenEditor(broadcast) {
    if (this.state.creating) {
      this.uiActions.openNotification('Please save or cancel your editing broadcast')
      return
    }

    this.setState({
      editorOpen: true,
      editingBroadcast: Object.assign({}, broadcast),
    })
  }

  handleKeyDownEsc(e) {
    // TODO: on ESC pressed
    if (e.which === 27) {
      this.handleCloseEditor()
    }
  }

  handleCloseEditor() {
    this.setState({
      editorOpen: false,
      editingBroadcast: {},
    })
  }

  renderBroadcastEditor() {
    return (
      <BroadcastEditor
        broadcast={this.state.editingBroadcast}
        handleCloseEditor={this.handleCloseEditor}
      />
    )
  }

  render() {
    const dialogActions = bindActionCreators(
      dialogActionCreators, this.props.dispatch)

    return (
      <div style={styles.container}>
        {
          !this.state.creating ? null :
            <BroadcastItem
              handleCloseEditor={() => this.setState({
                creating: false,
              })}
              broadcast={{}}
              expanded
              isFirst
              isLast
            />
        }
        {
          this.props.futureBroadcasts.map((b, idx) =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              handleEdit={() => { this.handleOpenEditor(b) }}
              handleCloseEditor={this.handleCloseEditor}
              handleSend={() => dialogActions.openSendBroadcast(b)}
              handleDelete={() => dialogActions.openDelBroadcast(b.id)}
              expandedIdx={this.state.futureBroadcastsExpandedIdx}
              isFirst={idx === 0}
              isLast={idx === this.props.futureBroadcasts.length - 1}
              expanded={b.id === this.state.editingBroadcast.id}
              isNext={!!this.props.futureBroadcasts[idx - 1] &&
                this.state.editingBroadcast.id === this.props.futureBroadcasts[idx - 1].id}
              isPrev={!!this.props.futureBroadcasts[idx + 1] &&
                this.state.editingBroadcast.id === this.props.futureBroadcasts[idx + 1].id}
            />
          )
        }
        {this.props.pastBroadcasts.length > 0 && <Subheader>History broadcasts</Subheader>}
        {
          this.props.pastBroadcasts.map((b, idx) =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              handleEdit={() => { this.handleOpenEditor(b) }}
              handleCloseEditor={this.handleCloseEditor}
              handleSend={() => dialogActions.openSendBroadcast(b)}
              handleDelete={() => dialogActions.openDelBroadcast(b.id)}
              isFirst={idx === 0}
              isLast={idx === this.props.pastBroadcasts.length - 1}
              expanded={b.id === this.state.editingBroadcast.id}
              isNext={!!this.props.pastBroadcasts[idx - 1] &&
                this.state.editingBroadcast.id === this.props.pastBroadcasts[idx - 1].id}
              isPrev={!!this.props.pastBroadcasts[idx + 1] &&
                this.state.editingBroadcast.id === this.props.pastBroadcasts[idx + 1].id}
            />
          )
        }
        <FloatingActionButton
          onClick={() => {
            if (this.state.editorOpen) {
              this.uiActions.openNotification('Please save or cancel the broadcast first')
              return
            }
            this.handleCloseEditor()
            this.setState({
              creating: true,
            })
          }}
          style={styles.floatButton}
        >
          <ContentAdd />
        </FloatingActionButton>
      </div>
    )
  }
}

Broadcast.propTypes = {
  dispatch: React.PropTypes.func,
  activeBotId: React.PropTypes.number,
  pastBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number,
  })),
  futureBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number,
  })),
}

const mapStateToProps = (state) => {
  const bs = orderBy(state.broadcasts.ids.map(
                       id => state.entities.broadcasts[id]),
                     ['scheduledTime'], ['desc'])
  const now = Math.floor(Date.now() / 1000)
  return {
    pastBroadcasts: bs.filter(b => b.scheduledTime <= now),
    futureBroadcasts: bs.filter(b => b.scheduledTime > now),
    activeBotId: state.bots.active,
  }
}

const ConnectedBroadcast = connect(
  mapStateToProps,
)(Broadcast)

export default ConnectedBroadcast
