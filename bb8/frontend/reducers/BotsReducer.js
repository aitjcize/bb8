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
    case types.BOTS_DELETE.SUCCESS:
      return state.withMutations((s) => {
        const id = action.payload
        s.set('active', -1)
        s.setIn(['listing', 'entities', 'bots', id.toString()], undefined)
        const idx = s.getIn(['listing', 'result']).indexOf(id)
        s.deleteIn(['listing', 'result', idx])
      })
    case types.BOTS_UPDATE.SUCCESS:
      return state.withMutations(() => {})
    case types.BOTS_SET_ACTIVE:
      return action.payload <= state.get('listing').get('result').size ?
        state.set('active', action.payload) : state
    default:
      return state
  }
}

export default BotsReducer
