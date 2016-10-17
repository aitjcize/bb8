import Immutable from 'immutable'

import types from '../constants/ActionTypes'


const INITIAL_STATE = Immutable.fromJS({
  active: -1,
  listing: {
    result: [],
    entities: {},
  },
})


// TODO(aitjcize): deal with error
function BotsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.BOTS_LIST.SUCCESS:
      return state.set('listing', action.payload)
    case types.BOTS_GET.SUCCESS:
      return state.withMutations((s) => {
        const payload = action.payload
        s.set('active', payload.result)
        s.mergeDeepIn(['listing', 'entities'], payload.entities)
      })
    case types.BOTS_CREATE.SUCCESS:
      return state.withMutations((s) => {
        const payload = action.payload
        s.set('active', payload.result)
        s.mergeDeepIn(['listing', 'entities'], payload.entities)
        s.setIn(['listing', 'result'],
                s.getIn(['listing', 'result']).push(payload.result))
      })
    case types.BOTS_UPDATE.SUCCESS:
      return state.withMutations(() => {})
    default:
      return state
  }
}

export default BotsReducer
