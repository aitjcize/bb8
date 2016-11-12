import types from '../constants/ActionTypes'

export const initializeApp = () => ({
  type: types.INITIALIZE_APP,
  payload: null,
})

export const openNotification = message => ({
  type: types.NOTIFICATION_OPEN,
  payload: message,
})

export const closeNotification = () => ({
  type: types.NOTIFICATION_CLOSE,
  payload: null,
})

// Accounts action creators

export const startLogin = (email, passwd) => ({
  type: types.ACCOUNTS_LOGIN.REQUEST,
  payload: {
    email,
    passwd,
  },
})

// Bots action creators

export const setActiveBot = botId => ({
  type: types.BOTS_SET_ACTIVE,
  payload: botId,
})

export const getAllBots = () => ({
  type: types.BOTS_LIST.REQUEST,
  payload: null,
})

export const getBot = botId => ({
  type: types.BOTS_GET,
  payload: botId,
})

export const createBot = bot => ({
  type: types.BOTS_CREATE.REQUEST,
  payload: bot,
})

export const updateBot = (botId, bot) => ({
  type: types.BOTS_UPDATE.REQUEST,
  payload: {
    botId,
    bot,
  },
})

export const delBot = botId => ({
  type: types.BOTS_DELETE.REQUEST,
  payload: botId,
})

// Platform action creators

export const getPlatforms = () => ({
  type: types.PLATFORMS_LIST.REQUEST,
  payload: null,
})

export const createPlatform = platform => ({
  type: types.PLATFORMS_CREATE.REQUEST,
  payload: platform,
})

export const delPlatform = platformId => ({
  type: types.PLATFORMS_DELETE.REQUEST,
  payload: platformId,
})

export const updatePlatform = (platformId, platform) => ({
  type: types.PLATFORMS_UPDATE.REQUEST,
  payload: {
    platformId,
    platform,
  },
})

// Broadcast action creators
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
