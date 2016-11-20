import Moment from 'moment'
import types from '../constants/ActionTypes'

export const closeDialog = () => ({
  type: types.DIALOG_CLOSE,
  payload: {},
})

export const openBroadcastDate = broadcast => ({
  type: types.DIALOG_BROADCAST_DATE.OPEN,
  payload: broadcast,
})

export const confirmBroadcastDate = (broadcast, date) => ({
  type: types.DIALOG_BROADCAST_DATE.CONFIRM,
  payload: Object.assign(
    broadcast,
    { scheduledTime: Moment(date).unix() }),
})

export const openSendBroadcast = broadcast => ({
  type: types.DIALOG_BROADCAST_SEND.OPEN,
  payload: broadcast,
})

export const confirmSendBroadcast = broadcast => ({
  type: types.DIALOG_BROADCAST_SEND.CONFIRM,
  payload: broadcast,
})

export const openDelBroadcast = broadcastId => ({
  type: types.DIALOG_BROADCAST_DEL.OPEN,
  payload: broadcastId,
})

export const confirmDelBroadcast = broadcastId => ({
  type: types.DIALOG_BROADCAST_DEL.CONFIRM,
  payload: broadcastId,
})
