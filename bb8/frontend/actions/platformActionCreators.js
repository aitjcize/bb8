import types from '../constants/ActionTypes'

export const getPlatforms = () => ({
  type: types.PLATFORMS_LIST.REQUEST,
  payload: null,
})

export const createPlatform = platform => ({
  type: types.PLATFORMS_CREATE.REQUEST,
  payload: platform,
})

export const updatePlatform = (platformId, platform) => ({
  type: types.PLATFORMS_UPDATE.REQUEST,
  payload: {
    platformId,
    platform,
  },
})

export const refreshPage = platform => ({
  type: types.PLATFORMS_REFRESH.REQUEST,
  payload: platform,
})
