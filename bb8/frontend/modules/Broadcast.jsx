import orderBy from 'lodash/orderBy'
import React from 'react'
import { connect } from 'react-redux'

import ContentAdd from 'material-ui/svg-icons/content/add'
import Dialog from 'material-ui/Dialog'
import FlatButton from 'material-ui/FlatButton'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import Subheader from 'material-ui/Subheader'

import { BroadcastItem, BroadcastEditor } from '../components/Broadcast'

import { getAllBroadcasts, updateBroadcast, delBroadcast } from '../actions/broadcastActionCreators'
import { openNotification } from '../actions/uiActionCreators'

const DIALOG_STATE = {
  CLOSE: 0,
  DELETE: 1,
  SEND: 2,
}

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
    this.handleOpenDeleteDialog = this.handleOpenDeleteDialog.bind(this)
    this.handleOpenSendDialog = this.handleOpenSendDialog.bind(this)
    this.handleConfirmDeleteDialog = this.handleConfirmDeleteDialog.bind(this)
    this.handleConfirmSendDialog = this.handleConfirmSendDialog.bind(this)
    this.handleCloseDialog = this.handleCloseDialog.bind(this)
    this.renderBroadcastEditor = this.renderBroadcastEditor.bind(this)
    this.handleKeyDownEsc = this.handleKeyDownEsc.bind(this)

    this.state = {
      dialogOpen: DIALOG_STATE.CLOSE,
      idInDialog: null,
      editorOpen: false,
      creating: false,
      editingBroadcast: { },
    }
  }


  componentWillMount() {
    this.props.dispatchGetAllBroadcasts(this.props.activeBotId)
  }

  componentDidMount() {
    window.addEventListener('keydown', this.handleKeyDownEsc)
    // window.addEventListener('mousedown', (e) => {
    // TODO: click empty field to end edit seasons.
    // })
  }

  componentWillUnmount() {
    window.removeEventListener('keydown', this.handleKeyDownEsc)
  }

  handleOpenEditor(broadcast) {
    if (this.state.creating) {
      this.props.dispatchShowNotification('Please save or cancel your editing broadcast')
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

  handleOpenDeleteDialog(id) {
    this.setState({
      dialogOpen: DIALOG_STATE.DELETE,
      idInDialog: id,
    })
  }

  handleOpenSendDialog(id) {
    this.setState({
      dialogOpen: DIALOG_STATE.SEND,
      idInDialog: id,
    })
  }

  handleConfirmDeleteDialog() {
    this.handleCloseDialog()
    this.props.dispatchDelBroadcast(this.state.idInDialog)
  }

  handleConfirmSendDialog() {
    this.handleCloseDialog()
    this.props.dispatchSendBroadcast(
      this.props.activeBotId,
      this.state.idInDialog,
      this.props.broadcasts[this.state.idInDialog])
  }

  handleCloseDialog() {
    this.setState({
      dialogOpen: DIALOG_STATE.CLOSE,
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
    const deleteActions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.handleCloseDialog}
      />,
      <FlatButton
        label="Delete"
        secondary
        keyboardFocused
        onTouchTap={this.handleConfirmDeleteDialog}
      />,
    ]

    const sendActions = [
      <FlatButton
        label="Cancel"
        primary
        onTouchTap={this.handleCloseDialog}
      />,
      <FlatButton
        label="Send Now"
        secondary
        keyboardFocused
        onTouchTap={this.handleConfirmSendDialog}
      />,
    ]

    return (
      <div style={styles.container}>
        <Dialog
          title={`Confirm ${this.state.dialogOpen === DIALOG_STATE.DELETE ? 'Delete' : 'Send'}`}
          actions={this.state.dialogOpen === DIALOG_STATE.DELETE ?
                   deleteActions : sendActions}
          modal={false}
          open={this.state.dialogOpen > DIALOG_STATE.CLOSE}
          onRequestClose={this.handleCloseDialog}
        >
          { this.state.dialogOpen === DIALOG_STATE.DELETE ?
            'Are you sure to delete this broadcast message?' :
            'Are you sure to send this broadcast message?' }
        </Dialog>
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
              handleDelete={() => this.handleOpenDeleteDialog(b.id)}
              handleCloseEditor={this.handleCloseEditor}
              handleSend={() => this.handleOpenSendDialog(b.id)}
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
              handleDelete={() => this.handleOpenDeleteDialog(b.id)}
              handleCloseEditor={this.handleCloseEditor}
              handleSend={() => this.handleOpenSendDialog(b.id)}
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
              this.props.dispatchShowNotification('Please save or cancel the broadcast first')
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
  dispatchGetAllBroadcasts: React.PropTypes.func,
  dispatchDelBroadcast: React.PropTypes.func,
  dispatchSendBroadcast: React.PropTypes.func,
  dispatchShowNotification: React.PropTypes.func,
  activeBotId: React.PropTypes.number,
  pastBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.Number,
  })),
  futureBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({
    id: React.PropTypes.Number,
  })),
  broadcasts: React.PropTypes.objectOf(React.PropTypes.shape({})),
}

const mapStateToProps = (state) => {
  const bs = orderBy(state.broadcasts.ids.map(
                       id => state.entities.broadcasts[id]),
                     ['scheduledTime'], ['desc'])
  const now = Math.floor(Date.now() / 1000)
  return {
    pastBroadcasts: bs.filter(b => b.scheduledTime <= now),
    futureBroadcasts: bs.filter(b => b.scheduledTime > now),
    broadcasts: state.entities.broadcasts,
    activeBotId: state.bots.active,
  }
}

const mapDispatchToProps = dispatch => ({
  dispatchGetAllBroadcasts(botId) {
    dispatch(getAllBroadcasts(botId))
  },
  dispatchShowNotification(message) {
    dispatch(openNotification(message))
  },
  dispatchDelBroadcast(broadcastId) {
    dispatch(delBroadcast(broadcastId))
  },
  dispatchSendBroadcast(botId, broadcastId, broadcast) {
    dispatch(updateBroadcast(broadcastId, {
      name: broadcast.name,
      scheduledTime: 0,
      messages: broadcast.messages,
      botId,
    }))
  },
})

const ConnectedBroadcast = connect(
  mapStateToProps,
  mapDispatchToProps,
)(Broadcast)

export default ConnectedBroadcast
