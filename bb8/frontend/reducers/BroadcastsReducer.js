import union from 'lodash/union'

import types from '../constants/ActionTypes'

const INITIAL_STATE = {
  ids: [],
}

function BroadcastReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.BROADCASTS_LIST.SUCCESS:
      return {
        ids: action.payload.result,
      }
    case types.BROADCASTS_CREATE.SUCCESS:
    case types.BROADCASTS_GET.SUCCESS:
      return {
        ids: union(state.ids, [action.payload.result]),
      }
    case types.BROADCASTS_DELETE.SUCCESS:
      return {
        ids: state.ids.filter(id => id !== action.payload),
      }
    case types.BROADCASTS_UPDATE.SUCCESS:
      return state
    default:
      return state
  }
}

export default BroadcastReducer
