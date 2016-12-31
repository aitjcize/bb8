import mergeWith from 'lodash/mergeWith'
import isArray from 'lodash/isArray'

const initialEntities = {
  bots: {},
  platforms: {},
}

// Updates an entity cache in response to any action with response.entities.
const EntitiesReducer = (state = initialEntities, action) => {
  if (action.payload && action.payload.entities) {
    return mergeWith({}, state,
      action.payload.entities, (objVal, srcVal) => (isArray(objVal) ? srcVal : undefined))
  }
  return state
}

export default EntitiesReducer
