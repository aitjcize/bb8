import { combineReducers } from 'redux-immutable'
import BotsReducer from './BotsReducer'

const rootReducer = combineReducers({
  bots: BotsReducer,
})

export default rootReducer
