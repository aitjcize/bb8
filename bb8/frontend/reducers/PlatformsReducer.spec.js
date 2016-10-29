import { normalize, arrayOf } from 'normalizr-immutable'
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
      PlatformsReducer(undefined, {}).toJS()
    ).toEqual({
      result: [],
      entities: {},
    })
  })

  it('should return the state with list of platforms', () => {
    expect(
      PlatformsReducer(undefined, {
        type: types.PLATFORMS_LIST.SUCCESS,
        payload: normalize(PLATFORMS_LISTING, arrayOf(Platform), {
          useMapsForEntityObjects: true
        }),
      }).toJS()
    ).toEqual({
      result: [1, 2, 3],
      entities: {
        platforms: {
          1: PLATFORMS_LISTING[0],
          2: PLATFORMS_LISTING[1],
          3: PLATFORMS_LISTING[2],
        }
      }
    })
  })

  it('should populate the platform entities with returned platform info', () => {
    expect(
      (() => {
        const state = PlatformsReducer(undefined, {
          type: types.PLATFORMS_LIST.SUCCESS,
          payload: normalize(PLATFORMS_LISTING, arrayOf(Platform), {
            useMapsForEntityObjects: true,
          }),
        })
        return PlatformsReducer(state, {
          type: types.PLATFORMS_GET.SUCCESS,
          payload: normalize(PLATFORMS[0], Platform, {
            useMapsForEntityObjects: true,
          })
        }).toJS()
      })()
    ).toEqual({
      result: [1, 2, 3],
      entities: {
        platforms: {
          45: PLATFORMS[0],
          1: PLATFORMS_LISTING[0],
          2: PLATFORMS_LISTING[1],
          3: PLATFORMS_LISTING[2],
        }
      }
    })
  })

  it('should remove the platform', () => {
    expect(
      (() => {
        const state = PlatformsReducer(undefined, {
          type: types.PLATFORMS_LIST.SUCCESS,
          payload: normalize(PLATFORMS_LISTING, arrayOf(Platform), {
            useMapsForEntityObjects: true,
          }),
        })
        return PlatformsReducer(state, {
          type: types.PLATFORMS_DELETE.SUCCESS,
          payload: 1,
        }).toJS()
      })()
    ).toEqual({
      result: [2, 3],
      entities: {
        platforms: {
          2: PLATFORMS_LISTING[1],
          3: PLATFORMS_LISTING[2],
        }
      }
    })
  })

  it('should add the newly created platform', () => {
    expect(
      PlatformsReducer(undefined, {
        type: types.PLATFORMS_CREATE.SUCCESS,
        payload: normalize(PLATFORMS[0], Platform, {
          useMapsForEntityObjects: true,
        }),
      }).toJS()
    ).toEqual({
      result: [45],
      entities: {
        platforms: {
          45: PLATFORMS[0],
        }
      }
    })
  })
})
