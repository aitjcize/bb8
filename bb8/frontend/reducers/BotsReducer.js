import union from 'lodash/union'

import types from '../constants/ActionTypes'


const INITIAL_STATE = {
  ids: [],
}


// TODO(aitjcize): deal with error
function BotsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.BOTS_LIST.SUCCESS:
      return {
        ids: action.payload.result,
      }
    case types.BOTS_GET.SUCCESS:
    case types.BOTS_CREATE.SUCCESS:
      return {
        ids: union(state.ids, [action.payload.result]),
      }
    case types.BOTS_DELETE.SUCCESS:
      return {
        ids: state.ids.filter(id => id !== action.payload),
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
