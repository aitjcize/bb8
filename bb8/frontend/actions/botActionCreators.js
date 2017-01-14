import types from '../constants/ActionTypes'

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

export const updateBot = (botId, botObj) => ({
  type: types.BOTS_UPDATE.REQUEST,
  payload: {
    botId,
    botObj,
  },
})

export const updateBotDefRevisions = (botId, botDef) => ({
  type: types.BOTS_UPDATE_DEFS.REQUEST,
  payload: {
    botId,
    botDef,
  },
})

export const deleteBot = botId => ({
  type: types.BOTS_DELETE.REQUEST,
  payload: botId,
})

export const deployBot = botId => ({
  type: types.BOTS_DEPLOY.REQUEST,
  payload: botId,
})
