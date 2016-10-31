import { normalize, arrayOf } from 'normalizr'
import { camelizeKeys } from 'humps'

import BroadcastsReducer from './BroadcastsReducer'
import { Broadcast } from '../constants/Schema'
import types from '../constants/ActionTypes'

const BROADCASTS_LISTING = camelizeKeys([
  {
    id: 1,
    name: 'broadcast 1',
    scheduled_time: 1477895132,
    status: 'Queued',
  },
  {
    id: 2,
    name: 'broadcast 1',
    scheduled_time: 1477895200,
    status: 'Sending',
  },
])

const BROADCASTS = camelizeKeys([
  {
    id: 1,
    name: 'broadcast 1',
    scheduled_time: 1477895132,
    status: 'Queued',
    messages: [],
  },
  {
    id: 1,
    name: 'broadcast 2',
    scheduled_time: 1477895200,
    status: 'Sending',
    messages: [],
  }
])

describe('Reducer for Broadcasts', () => {
  it('should return the initial state', () => {
    expect(
      BroadcastsReducer(undefined, {})
    ).toEqual({
      ids: [],
    })
  })

  it('should return the state with list of broadcasts', () => {
    expect(
      BroadcastsReducer(undefined, {
        type: types.BROADCASTS_LIST.SUCCESS,
        payload: normalize(BROADCASTS_LISTING, arrayOf(Broadcast)),
      })
    ).toEqual({
      ids: [1, 2],
    })
  })

  it('should return the id with newly created broadcast', () => {
    expect(
      BroadcastsReducer(undefined, {
        type: types.BROADCASTS_CREATE.SUCCESS,
        payload: normalize(BROADCASTS[0], Broadcast),
      })
    ).toEqual({
      ids: [1],
    })
  })

  it('should remove the broadcast', () => {
    expect(
      (() => {
        let state = BroadcastsReducer(undefined, {
          type: types.BROADCASTS_LIST.SUCCESS,
          payload: normalize(BROADCASTS_LISTING, arrayOf(Broadcast)),
        })
        return BroadcastsReducer(state, {
          type: types.BROADCASTS_DELETE.SUCCESS,
          payload: 1,
        })
      })()
    ).toEqual({
      ids: [2],
    })
  })
})
