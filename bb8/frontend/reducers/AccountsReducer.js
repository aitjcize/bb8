import Immutable from 'immutable'

import types from '../constants/ActionTypes'

const INITIAL_STATE = Immutable.fromJS({})


function AccountsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.ACCOUNTS_REGISTER.SUCCESS:
    case types.ACCOUNTS_LOGIN.SUCCESS:
      return Immutable.fromJS(action.payload)

    case types.ACCOUNTS_LOGOUT.SUCCESS:
      return Immutable.fromJS({})

    case types.ACCOUNTS_GET_ME.SUCCESS:
      return state.merge(action.payload)

    default:
      return state
  }
}

export default AccountsReducer
