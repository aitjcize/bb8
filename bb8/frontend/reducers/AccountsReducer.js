import merge from 'lodash/merge'

import types from '../constants/ActionTypes'

const INITIAL_STATE = {}


function AccountsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.ACCOUNTS_REGISTER.SUCCESS:
    case types.ACCOUNTS_LOGIN.SUCCESS:
      return Object.assign({}, action.payload)

    case types.ACCOUNTS_LOGOUT.SUCCESS:
      return {}

    case types.ACCOUNTS_GET_ME.SUCCESS:
      return merge({}, state, action.payload)

    default:
      return state
  }
}

export default AccountsReducer
