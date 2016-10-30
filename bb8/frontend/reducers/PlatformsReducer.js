import union from 'lodash/union'

import types from '../constants/ActionTypes'

const INITIAL_STATE = {
  ids: [],
}

function PlatformsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.PLATFORMS_LIST.SUCCESS:
      return {
        ids: action.payload.result,
      }

    case types.PLATFORMS_GET.SUCCESS:
      return {
        ids: union(state.ids, [action.payload.result]),
      }

    case types.PLATFORMS_CREATE.SUCCESS:
    case types.PLATFORMS_UPDATE.SUCCESS:
      return {
        ids: union(state.ids, [action.payload.result]),
      }

    case types.PLATFORMS_DELETE.SUCCESS:
      return {
        ids: state.ids.filter(id => id !== action.payload),
      }

    default:
      return state
  }
}

export default PlatformsReducer
