// This file is only for development use, import it
// and put it to the second arguments of createStore,
// and it will populate the initial state

import Immutable from 'immutable'
import { camelizeKeys } from 'humps'
import { normalize, arrayOf } from 'normalizr-immutable'

import types from './constants/ActionTypes'
import { Bot, Platform } from './constants/Schema'
import BotsReducer from './reducers/BotsReducer'
import PlatformsReducer from './reducers/PlatformsReducer'

const BOTS_LISTING = camelizeKeys([
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
])

const PLATFORMS_LISTING = camelizeKeys([{
  id: 1,
  bot_id: 1,
  name: 'test1',
  type_enum: 'Facebook',
  provider_ident: '12345678',
  config: {},
}, {
  id: 2,
  bot_id: 1,
  name: 'test1',
  type_enum: 'Line',
  provider_ident: 'test1.composeai',
  config: {},
}, {
  id: 3,
  bot_id: null,
  name: 'test1',
  type_enum: 'Facebook',
  provider_ident: '23456',
  config: {},
}])

const initialState = Immutable.Map()
  .set('bots', BotsReducer(undefined, {
    type: types.BOTS_LIST.SUCCESS,
    payload: normalize(BOTS_LISTING, arrayOf(Bot), { useMapsForEntityObjects: true }),
  }))
  .set('platforms', PlatformsReducer(undefined, {
    type: types.PLATFORMS_LIST.SUCCESS,
    payload: normalize(PLATFORMS_LISTING, arrayOf(Platform), { useMapsForEntityObjects: true }),
  }))

export default initialState
