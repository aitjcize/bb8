import orderBy from 'lodash/orderBy'
import React from 'react'
import { connect } from 'react-redux'

import ContentAdd from 'material-ui/svg-icons/content/add'
// import Dialog from 'material-ui/Dialog'
// import Drawer from 'material-ui/Drawer'
// import FlatButton from 'material-ui/FlatButton'
import FloatingActionButton from 'material-ui/FloatingActionButton'
import Subheader from 'material-ui/Subheader'

import { BroadcastItem, BroadcastEditor } from '../components/Broadcast'

import { getAllBroadcasts, updateBroadcast, delBroadcast } from '../actions'

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

    this.state = {
      dialogOpen: DIALOG_STATE.CLOSE,
      idInDialog: null,
      editorOpen: false,
      editingBroadcast: { },
    }
  }

  componentWillMount() {
    this.props.dispatchGetAllBroadcasts(this.props.activeBotId)
  }

  handleOpenEditor(broadcast) {
    this.setState({
      editorOpen: true,
      editingBroadcast: Object.assign({}, broadcast),
    })

    return this.state.editorOpen
  }

  handleCloseEditor() {
    this.setState({ editorOpen: false })
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
    /*
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
    */

    return (
      <div style={styles.container}>
        {
      /*
        <Dialog
          title={`Confirm ${this.state.dialogOpen === DIALOG_STATE.DELETE ? 'Delete' : 'Send'}`}
          actions={this.state.dialogOpen === DIALOG_STATE.DELETE ?
                   deleteActions : sendActions}
          modal={false}
          open={this.state.dialogOpen > 0}
          onRequestClose={this.handleCloseDialog}
        >
          { this.state.dialogOpen === DIALOG_STATE.DELETE ?
            'Are you sure to delete this broadcast message?' :
            'Are you sure to send this broadcast message?' }
        </Dialog>
        <Drawer
          docked={false}
          width={500}
          open={this.state.editorOpen}
          openSecondary
          onRequestChange={editorOpen => this.setState({ editorOpen })}
        >
          <BroadcastEditor
            broadcast={this.state.editingBroadcast}
            handleCloseEditor={this.handleCloseEditor}
          />
        </Drawer>
        */}
        {
          this.props.futureBroadcasts.map((b, idx) =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              handleEdit={() => {
                this.setState({
                  futureBroadcastsExpandedIdx: idx,
                  pastBroadcastsExpandedIdx: undefined,
                })
                this.handleOpenEditor(b)
              }}
              handleDelete={() => this.handleOpenDeleteDialog(b.id)}
              handleSend={() => this.handleOpenSendDialog(b.id)}
              expandedIdx={this.state.futureBroadcastsExpandedIdx}
              idx={idx}
              lastIdx={this.props.futureBroadcasts.length - 1}
            />
          )
        }
        <Subheader>History broadcasts</Subheader>
        {
          this.props.pastBroadcasts.map((b, idx) =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              handleEdit={() => {
                this.setState({
                  futureBroadcastsExpandedIdx: undefined,
                  pastBroadcastsExpandedIdx: idx,
                })
                this.handleOpenEditor(b)
              }}
              handleDelete={() => this.handleOpenDeleteDialog(b.id)}
              handleSend={() => this.handleOpenSendDialog(b.id)}
              expandedIdx={this.state.pastBroadcastsExpandedIdx}
              idx={idx}
              lastIdx={this.props.pastBroadcasts.length - 1}
            />
          )
        }
        <FloatingActionButton
          onClick={() => this.handleOpenEditor({ broadcast: {} })}
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
  activeBotId: React.PropTypes.number,
  pastBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({})),
  futureBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({})),
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
