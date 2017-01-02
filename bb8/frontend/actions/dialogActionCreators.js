import Moment from 'moment'
import types from '../constants/ActionTypes'

export const closeDialog = () => ({
  type: types.DIALOG_CLOSE,
  payload: {},
})

/* Bot Dialog */

export const openBotCreate = () => ({
  type: types.DIALOG_BOT_CREATE.OPEN,
  payload: null,
})

export const confirmBotCreate = bot => ({
  type: types.DIALOG_BOT_CREATE.CONFIRM,
  payload: bot,
})

export const openBotUpdate = (botId, name, description) => ({
  type: types.DIALOG_BOT_UPDATE.OPEN,
  payload: {
    botId, name, description,
  },
})

export const confirmBotUpdate = bot => ({
  type: types.DIALOG_BOT_UPDATE.CONFIRM,
  payload: bot,
})

export const openBotDelete = botId => ({
  type: types.DIALOG_BOT_DELETE.OPEN,
  payload: botId,
})

export const confirmBotDelete = botId => ({
  type: types.DIALOG_BOT_DELETE.CONFIRM,
  payload: botId,
})

/* Broadcast Dialog */

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

/* Platform Dialog */

export const openDelPlatform = platformId => ({
  type: types.DIALOG_PLATFORM_DEL.OPEN,
  payload: platformId,
})

export const confirmDelPlatform = platformId => ({
  type: types.DIALOG_PLATFORM_DEL.CONFIRM,
  payload: platformId,
})

export const openCreatePlatform = () => ({
  type: types.DIALOG_PLATFORM_CREATE.OPEN,
})

export const openUpdatePlatform = platform => ({
  type: types.DIALOG_PLATFORM_UPDATE.OPEN,
  payload: platform,
})

export const confirmCreatePlatform = platform => ({
  type: types.DIALOG_PLATFORM_CREATE.CONFIRM,
  payload: platform,
})

export const confirmUpdatePlatform = platform => ({
  type: types.DIALOG_PLATFORM_UPDATE.CONFIRM,
  payload: platform,
})
