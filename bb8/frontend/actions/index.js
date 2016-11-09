import types from '../constants/ActionTypes'

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
