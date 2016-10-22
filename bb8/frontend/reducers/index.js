import Immutable from 'immutable'
import { reducer as form } from 'redux-form/immutable'
import { combineReducers } from 'redux-immutable'
import { LOCATION_CHANGE } from 'react-router-redux'
import AccountsReducer from './AccountsReducer'
import BotsReducer from './BotsReducer'

const initialState = Immutable.fromJS({
  locationBeforeTransitions: null,
})

function routingReducer(state = initialState, action) {
  if (action.type === LOCATION_CHANGE) {
    return state.merge({
      locationBeforeTransitions: action.payload,
    })
  }
  return state
}

const rootReducer = combineReducers({
  form,
  bots: BotsReducer,
  account: AccountsReducer,
  routing: routingReducer,
})

export default rootReducer
