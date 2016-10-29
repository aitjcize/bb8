import Immutable from 'immutable'

import types from '../constants/ActionTypes'

const INITIAL_STATE = Immutable.fromJS({
  result: [],
  entities: {},
})


function PlatformsReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case types.PLATFORMS_LIST.SUCCESS:
      return Immutable.fromJS(action.payload)

    case types.PLATFORMS_GET.SUCCESS:
      return state.withMutations((s) => {
        const payload = action.payload
        s.mergeDeepIn(['entities'], payload.entities)
      })

    case types.PLATFORMS_CREATE.SUCCESS:
      return state.withMutations((s) => {
        const payload = action.payload
        s.set('result', s.get('result').push(payload.result))
        s.mergeDeepIn(['entities'], payload.entities)
      })

    case types.PLATFORMS_DELETE.SUCCESS:
      return state.withMutations((s) => {
        const id = action.payload
        s.setIn(['entities', 'platforms', id.toString()], undefined)
        const idx = s.get('result').indexOf(id)
        s.deleteIn(['result', idx])
      })

    case types.PLATFORMS_UPDATE.SUCCESS:
      return state.withMutations((s) => {
        const payload = action.payload

        const idx = s.get('result').indexOf(payload.result)
        if (idx === -1) {
          s.set('result', s.get('result').push(payload.result))
        }
        s.mergeDeepIn(['entities'], payload.entities)
      })

    default:
      return state
  }
}

export default PlatformsReducer
