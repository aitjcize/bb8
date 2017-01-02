import union from 'lodash/union'

import types from '../constants/ActionTypes'


const INITIAL_STATE = {
  active: -1,
  ids: [],
}


// TODO(aitjcize): deal with error
function BotsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.BOTS_LIST.SUCCESS:
      return {
        active: action.payload.result.indexOf(state.active) >= 0 ? state.active :
          action.payload.result[0] || -1,
        ids: action.payload.result,
      }
    case types.BOTS_GET.SUCCESS:
    case types.BOTS_CREATE.SUCCESS:
      return {
        active: action.payload.result,
        ids: union(state.ids, [action.payload.result]),
      }
    case types.BOTS_DELETE.SUCCESS:
      return {
        active: -1,
        ids: state.ids.filter(id => id !== action.payload),
      }
    case types.BOTS_SET_ACTIVE:
      return {
        ...state,
        active: state.ids.indexOf(action.payload) >= 0 ?
          action.payload : state.active,
      }
    case types.BOTS_UPDATE.SUCCESS:
      return {
        ...state,
        payload: action.payload,
      }
    default:
      return state
  }
}

export default BotsReducer
