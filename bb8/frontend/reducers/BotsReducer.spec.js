import { normalize, arrayOf } from 'normalizr'
import { camelizeKeys } from 'humps'

import types from '../constants/ActionTypes'
import { Bot } from '../constants/Schema'

import BotsReducer from './BotsReducer'


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

const BOTS = camelizeKeys([
  {
    id: 1,
    name: 'Bot 1',
    description: 'Bot 1',
    interaction_timeout: 120,
    admin_interaction_timeout: 180,
    session_timeout: 86400,
    ga_id: '',
    settings: {},
    staging: null,
  },
  {
    id: 2,
    name: 'Bot 2',
    description: 'Bot 2',
    interaction_timeout: 120,
    admin_interaction_timeout: 180,
    session_timeout: 86400,
    ga_id: '',
    settings: {},
    staging: null,
  },
])

describe('Reducer for Bots', () => {
  it('should return the initial state', () => {
    expect(
      BotsReducer(undefined, {})
    ).toEqual({
      active: -1,
      ids: [],
    })
  })

  it('should return the state with list of bots', () => {
    expect(
      BotsReducer(undefined, {
        type: types.BOTS_LIST.SUCCESS,
        payload: normalize(BOTS_LISTING, arrayOf(Bot)),
      })
    ).toEqual({
      active: -1,
      ids: [1, 2],
    })
  })

  it('should populate the bot entities with returned bot info', () => {
    expect(
      (() => {
        let state = BotsReducer(undefined, {
          type: types.BOTS_LIST.SUCCESS,
          payload: normalize(BOTS_LISTING, arrayOf(Bot)),
        })
        return BotsReducer(state, {
          type: types.BOTS_GET.SUCCESS,
          payload: normalize(BOTS[0], Bot),
        })
      })()
    ).toEqual({
      active: 1,
      ids: [1, 2],
    })
  })

  it('should return the state with newly created bot', () => {
    expect(
      BotsReducer(undefined, {
        type: types.BOTS_CREATE.SUCCESS,
        payload: normalize(BOTS[0], Bot),
      })
    ).toEqual({
      active: 1,
      ids: [1],
    })
  })

  it('should remove the bot from record', () => {
    expect(
      (() => {
        let state = BotsReducer(undefined, {
          type: types.BOTS_LIST.SUCCESS,
          payload: normalize(BOTS_LISTING, arrayOf(Bot)),
        })
        return BotsReducer(state, {
          type: types.BOTS_DELETE.SUCCESS,
          payload: 1,
        })
      })()
    ).toEqual({
      active: -1,
      ids: [2],
    })
  })

  it('should not update the active id', () => {
    expect(
      BotsReducer(undefined, {
        type: types.BOTS_SET_ACTIVE,
        payload: 5,
      })
    ).toEqual({
      active: -1,
      ids: [],
    })
  })

  it('should update the active id', () => {
    let state = BotsReducer(undefined, {
      type: types.BOTS_LIST.SUCCESS,
      payload: normalize(BOTS_LISTING, arrayOf(Bot)),
    })
    expect(
      BotsReducer(state, {
        type: types.BOTS_SET_ACTIVE,
        payload: 1,
      })
    ).toEqual({
      active: 1,
      ids: [1, 2],
    })
  })
})
