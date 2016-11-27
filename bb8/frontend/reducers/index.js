import { reducer as form } from 'redux-form'
import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'
import mergeWith from 'lodash/mergeWith'
import isArray from 'lodash/isArray'

import AccountsReducer from './AccountsReducer'
import BotsReducer from './BotsReducer'
import BroadcastsReducer from './BroadcastsReducer'
import BroadcastEditorReducer from './BroadcastEditorReducer'
import DialogReducer from './DialogReducer'
import NotificationReducer from './NotificationReducer'
import PlatformsReducer from './PlatformsReducer'

const initialEntities = {
  bots: {},
  platforms: {},
}

// Updates an entity cache in response to any action with response.entities.
const entities = (state = initialEntities, action) => {
  if (action.payload && action.payload.entities) {
    return mergeWith({}, state,
      action.payload.entities, (objVal, srcVal) => (isArray(objVal) ? srcVal : undefined))
  }
  return state
}

const rootReducer = combineReducers({
  entities,
  form,
  account: AccountsReducer,
  bots: BotsReducer,
  broadcasts: BroadcastsReducer,
  broadcastEditor: BroadcastEditorReducer,
  dialog: DialogReducer,
  notification: NotificationReducer,
  platforms: PlatformsReducer,
  routing: routerReducer,
})

export default rootReducer
