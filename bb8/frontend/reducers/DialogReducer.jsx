import React from 'react'
import types from '../constants/ActionTypes'

import BotDialog from '../components/Dialog/BotDialog'
import BotDeleteDialog from '../components/Dialog/BotDeleteDialog'
import BroadcastDateDialog from '../components/Dialog/BroadcastDateDialog'
import BroadcastSendDialog from '../components/Dialog/BroadcastSendDialog'
import BroadcastDelDialog from '../components/Dialog/BroadcastDelDialog'
import PlatformDelDialog from '../components/Dialog/PlatformDelDialog'
import PlatformDialog from '../components/Dialog/PlatformDialog'

const DEFAULT_COMPONENT = null

const INITIAL_STATE = {
  open: false,
  component: DEFAULT_COMPONENT,
  payload: {},
}

function DialogReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.DIALOG_PLATFORM_UPDATE.OPEN:
    case types.DIALOG_PLATFORM_CREATE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <PlatformDialog />,
      }
    case types.DIALOG_BOT_CREATE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BotDialog />,
      }
    case types.DIALOG_BOT_UPDATE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BotDialog />,
      }
    case types.DIALOG_BOT_DELETE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BotDeleteDialog />,
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
    case types.DIALOG_PLATFORM_DEL.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <PlatformDelDialog />,
      }
    case types.DIALOG_CLOSE:
      return INITIAL_STATE
    default:
      return state
  }
}

export default DialogReducer
