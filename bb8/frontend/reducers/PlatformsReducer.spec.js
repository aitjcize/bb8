import { normalize, arrayOf } from 'normalizr'
import { camelizeKeys } from 'humps'

import types from '../constants/ActionTypes'
import { Platform } from '../constants/Schema'

import PlatformsReducer from './PlatformsReducer'

const PLATFORMS_LISTING = camelizeKeys([{
  id: 1,
  bot_id: 1,
  name: 'test1',
  type_enum: 'Facebook',
  provider_ident: '12345678',
  config: null,
}, {
  id: 2,
  bot_id: 1,
  name: 'test1',
  type_enum: 'Line',
  provider_ident: 'test1.composeai',
  config: null,
}, {
  id: 3,
  bot_id: null,
  name: 'test1',
  type_enum: 'Facebook',
  provider_ident: '23456',
  config: null,
}])

const PLATFORMS = camelizeKeys([{
  id: 45,
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


describe('Reducer for platforms', () => {
  it('should return the initial state', () => {
    expect(
      PlatformsReducer(undefined, {})
    ).toEqual({
      ids: [],
    })
  })

  it('should return the state with list of platforms', () => {
    expect(
      PlatformsReducer(undefined, {
        type: types.PLATFORMS_LIST.SUCCESS,
        payload: normalize(PLATFORMS_LISTING, arrayOf(Platform)),
      })
    ).toEqual({
      ids: [1, 2, 3],
    })
  })

  it('should populate the platform entities with returned platform info', () => {
    expect(
      (() => {
        const state = PlatformsReducer(undefined, {
          type: types.PLATFORMS_LIST.SUCCESS,
          payload: normalize(PLATFORMS_LISTING, arrayOf(Platform)),
        })
        return PlatformsReducer(state, {
          type: types.PLATFORMS_GET.SUCCESS,
          payload: normalize(PLATFORMS[0], Platform), 
        })
      })()
    ).toEqual({
      ids: [1, 2, 3, 45],
    })
  })

  it('should remove the platform', () => {
    expect(
      (() => {
        const state = PlatformsReducer(undefined, {
          type: types.PLATFORMS_LIST.SUCCESS,
          payload: normalize(PLATFORMS_LISTING, arrayOf(Platform)), 
        })
        return PlatformsReducer(state, {
          type: types.PLATFORMS_DELETE.SUCCESS,
          payload: 1,
        })
      })()
    ).toEqual({
      ids: [2, 3],
    })
  })

  it('should add the newly created platform', () => {
    expect(
      PlatformsReducer(undefined, {
        type: types.PLATFORMS_CREATE.SUCCESS,
        payload: normalize(PLATFORMS[0], Platform),
      })
    ).toEqual({
      ids: [45],
    })
  })
})
