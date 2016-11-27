import types from '../constants/ActionTypes'

const INITIAL_STATE = {
  open: false,
  broadcastId: null,
  broadcast: { },
}

function BroadcastEditorReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.BROADCAST_EDITOR_OPEN:
      return {
        open: true,
        broadcastId: action.payload && action.payload.id,
        broadcast: action.payload,
      }
    case types.BROADCAST_EDITOR_CLOSE:
      return INITIAL_STATE
    default:
      return state
  }
}

export default BroadcastEditorReducer
