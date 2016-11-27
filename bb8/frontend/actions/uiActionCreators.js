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
