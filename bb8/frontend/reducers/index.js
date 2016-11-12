import { reducer as form } from 'redux-form'
import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import merge from 'lodash/merge'

import AccountsReducer from './AccountsReducer'
import BotsReducer from './BotsReducer'
import BroadcastsReducer from './BroadcastsReducer'
import NotificationReducer from './NotificationReducer'
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
  entities,
  form,
  account: AccountsReducer,
  bots: BotsReducer,
  broadcasts: BroadcastsReducer,
  notification: NotificationReducer,
  platforms: PlatformsReducer,
  routing: routerReducer,
})

export default rootReducer
