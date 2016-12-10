import types from '../constants/ActionTypes'

// eslint-disable-next-line import/prefer-default-export
export const refreshFacebookPages = () => ({
  type: types.FB_REFRESH_PAGES.REQUEST,
  payload: null,
})
