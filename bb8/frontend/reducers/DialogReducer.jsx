import React from 'react'
import types from '../constants/ActionTypes'

import BotCreateDialog from '../components/Dialog/BotCreateDialog'
import BroadcastDateDialog from '../components/Dialog/BroadcastDateDialog'
import BroadcastSendDialog from '../components/Dialog/BroadcastSendDialog'
import BroadcastDelDialog from '../components/Dialog/BroadcastDelDialog'

const DEFAULT_COMPONENT = null

const INITIAL_STATE = {
  open: false,
  component: DEFAULT_COMPONENT,
  payload: {},
}

function DialogReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.DIALOG_BOT_CREATE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BotCreateDialog />,
      }
    case types.DIALOG_BROADCAST_DATE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BroadcastDateDialog />,
      }
    case types.DIALOG_BROADCAST_SEND.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BroadcastSendDialog />,
      }
    case types.DIALOG_BROADCAST_DEL.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BroadcastDelDialog />,
      }
    case types.DIALOG_CLOSE:
      return INITIAL_STATE

    default:
      return state
  }
}

export default DialogReducer