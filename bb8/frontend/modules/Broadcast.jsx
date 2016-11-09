import orderBy from 'lodash/orderBy'
import React from 'react'
import { connect } from 'react-redux'

import ContentAdd from 'material-ui/svg-icons/content/add'
import Dialog from 'material-ui/Dialog'
import Drawer from 'material-ui/Drawer'
import FlatButton from 'material-ui/FlatButton'
import FloatingActionButton from 'material-ui/FloatingActionButton'

import BroadcastItem from '../components/BroadcastItem'
import BroadcastEditor from '../components/BroadcastEditor'
import { getAllBroadcasts, updateBroadcast, delBroadcast } from '../actions'

const DIALOG_STATE = {
  CLOSE: 0,
  DELETE: 1,
  SEND: 2,
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

    this.state = {
      dialogOpen: DIALOG_STATE.CLOSE,
      idInDialog: null,
      editorOpen: false,
      editingBroadcast: { },
    }
  }

  componentWillMount() {
    this.props.dispatchGetAllBroadcasts(1)
  }

  handleOpenEditor(broadcast) {
    this.setState({
      editorOpen: true,
      editingBroadcast: Object.assign({}, broadcast),
    })
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
      this.state.idInDialog,
      this.props.broadcasts[this.state.idInDialog])
  }

  handleCloseDialog() {
    this.setState({
      dialogOpen: DIALOG_STATE.CLOSE,
    })
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
      <div>
        <Dialog
          title="Confirm Delete"
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
        {
          this.props.futureBroadcasts.map(b =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              handleEdit={() => this.handleOpenEditor(b)}
              handleDelete={() => this.handleOpenDeleteDialog(b.id)}
              handleSend={() => this.handleOpenSendDialog(b.id)}
            />
          )
        }
        <div> this is a line, below is past broadcast </div>
        {
          this.props.pastBroadcasts.map(b =>
            <BroadcastItem
              key={b.id}
              broadcast={b}
              handleEdit={() => this.handleOpenEditor(b)}
              handleDelete={() => this.handleOpenDeleteDialog(b.id)}
              handleSend={() => this.handleOpenSendDialog(b.id)}
            />
          )
        }
        <FloatingActionButton
          onClick={() => this.handleOpenEditor({ broadcast: {} })}
          className="b-add-platform-btn"
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
  pastBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({})),
  futureBroadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({})),
  broadcasts: React.PropTypes.arrayOf(React.PropTypes.shape({})),
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
  }
}

const mapDispatchToProps = dispatch => ({
  dispatchGetAllBroadcasts(botId) {
    dispatch(getAllBroadcasts(botId))
  },
  dispatchDelBroadcast(broadcastId) {
    dispatch(delBroadcast(broadcastId))
  },
  dispatchSendBroadcast(broadcastId, broadcast) {
    dispatch(updateBroadcast(broadcastId, {
      name: broadcast.name,
      scheduledTime: 0,
      botId: 6,
      messages: broadcast.messages,
    }))
  },
})

const ConnectedBroadcast = connect(
  mapStateToProps,
  mapDispatchToProps,
)(Broadcast)

export default ConnectedBroadcast
