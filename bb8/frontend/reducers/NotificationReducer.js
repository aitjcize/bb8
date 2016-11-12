import types from '../constants/ActionTypes'

const INITIAL_STATE = {
  open: false,
  message: '',
}

function NotificationReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.NOTIFICATION_OPEN:
      return {
        open: true,
        message: action.payload,
      }
    case types.NOTIFICATION_CLOSE:
      return {
        open: false,
        message: '',
      }
    default:
      return state
  }
}

export default NotificationReducer
