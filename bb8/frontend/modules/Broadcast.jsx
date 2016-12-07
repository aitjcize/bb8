import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import orderBy from 'lodash/orderBy'

import ContentAdd from 'material-ui/svg-icons/content/add'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import Subheader from 'material-ui/Subheader'

import { BroadcastItem } from '../components/Broadcast'
import * as broadcastActionCreators from '../actions/broadcastActionCreators'
import * as uiActionCreators from '../actions/uiActionCreators'

const styles = {
  container: {
    padding: '1em',
  },
  floatButton: {
    position: 'fixed',
    right: 0,
    bottom: 0,
    margin: '2.5em',
  },
}

class Broadcast extends React.Component {
  constructor(props) {
    super(props)

    this.handleKeyDownEsc = this.handleKeyDownEsc.bind(this)

    this.broadcastActions = bindActionCreators(
      broadcastActionCreators, this.props.dispatch)
    this.uiActions = bindActionCreators(
      uiActionCreators, this.props.dispatch)
  }


  componentWillMount() {
    this.broadcastActions.getAllBroadcasts(this.props.activeBotId)
  }

  componentDidMount() {
    window.addEventListener('keydown', this.handleKeyDownEsc)
  }

  componentWillUnmount() {
    window.removeEventListener('keydown', this.handleKeyDownEsc)
  }

  handleKeyDownEsc(e) {
    // TODO: on ESC pressed
    if (e.which === 27) {
      this.broadcastActions.closeBroadcastEditor()
    }
  }

  render() {
    return (
      <div style={styles.container}>
        {
          this.props.editor.open && !this.props.editor.broadcastId &&
            <BroadcastItem
              broadcast={{}}
              expanded={!this.props.editor.broadcastId}
              isFirst
              isLast
            />
        }
        {
          this.props.futureBroadcasts.map((b, idx) =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              isFirst={idx === 0}
              isLast={idx === this.props.futureBroadcasts.length - 1}
              expanded={b.id === this.props.editor.broadcastId}
              isNext={!!this.props.futureBroadcasts[idx - 1] &&
                this.props.editor.broadcastId === this.props.futureBroadcasts[idx - 1].id}
              isPrev={!!this.props.futureBroadcasts[idx + 1] &&
                this.props.editor.broadcastId === this.props.futureBroadcasts[idx + 1].id}
            />
          )
        }
        {
          this.props.pastBroadcasts.length > 0 &&
            <Subheader> History Broadcasts </Subheader>
        }
        {
          this.props.pastBroadcasts.map((b, idx) =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              isFirst={idx === 0}
              isLast={idx === this.props.pastBroadcasts.length - 1}
              expanded={b.id === this.props.editor.broadcastId}
              isNext={!!this.props.pastBroadcasts[idx - 1] &&
                this.props.editor.broadcastId === this.props.pastBroadcasts[idx - 1].id}
              isPrev={!!this.props.pastBroadcasts[idx + 1] &&
                this.props.editor.broadcastId === this.props.pastBroadcasts[idx + 1].id}
            />
          )
        }
        <FloatingActionButton
          onClick={() => {
            if (this.props.editor.open) {
              this.uiActions.openNotification('Please save or cancel the broadcast first')
              return
            }
            this.broadcastActions.openBroadcastEditor()
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
  dispatch: React.PropTypes.func.isRequired,
  activeBotId: React.PropTypes.number,
  pastBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number,
  })),
  futureBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.number,
  })),
  editor: React.PropTypes.shape({
    open: React.PropTypes.bool.isRequired,
    broadcastId: React.PropTypes.number,
    broadcast: React.PropTypes.shape({}),
  }).isRequired,
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
    editor: state.broadcastEditor,
  }
}

const ConnectedBroadcast = connect(
  mapStateToProps,
)(Broadcast)

export default ConnectedBroadcast
