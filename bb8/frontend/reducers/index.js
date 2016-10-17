import { combineReducers } from 'redux-immutable'
import AccountsReducer from './AccountsReducer'
import BotsReducer from './BotsReducer'

const rootReducer = combineReducers({
  bots: BotsReducer,
  account: AccountsReducer,
})

export default rootReducer
