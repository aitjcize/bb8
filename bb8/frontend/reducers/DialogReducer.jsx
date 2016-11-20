import React from 'react'
import types from '../constants/ActionTypes'

import BroadcastDateDialog from '../components/Dialog/BroadcastDateDialog'

const DEFAULT_COMPONENT = null

const INITIAL_STATE = {
  open: false,
  component: DEFAULT_COMPONENT,
  payload: {},
}

function DialogReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.DIALOG_BROADCAST_DATE.OPEN:
      return {
        open: true,
        payload: action.payload,
        component: <BroadcastDateDialog />,
      }
    case types.DIALOG_CLOSE:
      return INITIAL_STATE

    default:
      return state
  }
}

export default DialogReducer
