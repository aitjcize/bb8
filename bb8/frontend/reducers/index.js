import { reducer as form } from 'redux-form'
import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import merge from 'lodash/merge'

import AccountsReducer from './AccountsReducer'
import BotsReducer from './BotsReducer'
import BroadcastsReducer from './BroadcastsReducer'
import PlatformsReducer from './PlatformsReducer'

const initialEntities = {
  bots: {},
  platforms: {},
}

// Updates an entity cache in response to any action with response.entities.
const entities = (state = initialEntities, action) => {
  if (action.payload && action.payload.entities) {
    return merge({}, state, action.payload.entities)
  }
  return state
}

const rootReducer = combineReducers({
  form,
  entities,
  bots: BotsReducer,
  broadcasts: BroadcastsReducer,
  platforms: PlatformsReducer,
  account: AccountsReducer,
  routing: routerReducer,
})

export default rootReducer
