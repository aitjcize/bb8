// This file is only for development use, import it
// and put it to the second arguments of createStore,
// and it will populate the initial state

import Immutable from 'immutable'
import { normalize, arrayOf } from 'normalizr-immutable'
import types from './constants/ActionTypes'
import { Bot } from './constants/Schema'
import BotsReducer from './reducers/BotsReducer'

const BOTS_LISTING = [
  {
    id: 1,
    name: 'Bot 1',
    description: 'Bot 1',
    interaction_timeout: null,
    admin_interaction_timeout: null,
    session_timeout: null,
    ga_id: null,
    settings: null,
    staging: null,
  },
  {
    id: 2,
    name: 'Bot 2',
    description: 'Bot 2',
    interaction_timeout: null,
    admin_interaction_timeout: null,
    session_timeout: null,
    ga_id: null,
    settings: null,
    staging: null,
  },
]

const initialState = Immutable.Map().set('bots', BotsReducer(undefined, {
  type: types.BOTS_LIST.SUCCESS,
  payload: normalize(BOTS_LISTING, arrayOf(Bot)),
}))

export default initialState
