import { reducer as form } from 'redux-form'
import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'

import AccountsReducer from './AccountsReducer'
import BotsReducer from './BotsReducer'
import BroadcastsReducer from './BroadcastsReducer'
import BroadcastEditorReducer from './BroadcastEditorReducer'
import DialogReducer from './DialogReducer'
import EntitiesReducer from './EntitiesReducer'
import NotificationReducer from './NotificationReducer'
import PlatformsReducer from './PlatformsReducer'

const rootReducer = combineReducers({
  form,
  account: AccountsReducer,
  bots: BotsReducer,
  broadcastEditor: BroadcastEditorReducer,
  broadcasts: BroadcastsReducer,
  dialog: DialogReducer,
  entities: EntitiesReducer,
  notification: NotificationReducer,
  platforms: PlatformsReducer,
  routing: routerReducer,
})

export default rootReducer
