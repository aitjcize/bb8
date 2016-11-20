import types from '../constants/ActionTypes'

export const getAllBroadcasts = botId => ({
  type: types.BROADCASTS_LIST.REQUEST,
  payload: botId,
})

export const createBroadcast = broadcast => ({
  type: types.BROADCASTS_CREATE.REQUEST,
  payload: broadcast,
})

export const updateBroadcast = (broadcastId, broadcast) => ({
  type: types.BROADCASTS_UPDATE.REQUEST,
  payload: {
    broadcastId,
    broadcast,
  },
})

export const delBroadcast = broadcastId => ({
  type: types.BROADCASTS_DELETE.REQUEST,
  payload: broadcastId,
})
