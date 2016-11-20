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
