import { routerReducer as routing } from 'react-router-redux';
import { reducer as reduxFormReducer } from 'redux-form';
import { combineReducers } from 'redux';
import {
  LOGIN,
  LOGOUT,
  BOTS_GET_ALL,
  SET_ACTIVE_BOT,
  UPDATE_BOT_STAGING,
} from '../actions';


function account(state = null, action) {
  switch (action.type) {
    case LOGIN.SUCCESS:
      return action.payload;

    case LOGOUT:
      return null;

    default:
      return state;
  }
}

function bot(state = {}, action) {
  const { id, staging } = action.payload || {};
  const { bots, active } = state;

  switch (action.type) {
    case BOTS_GET_ALL:
      return {
        active: active || action.payload[0].id,
        bots: action.payload,
      };

    case UPDATE_BOT_STAGING:
      bots[id].staging = staging;
      return {
        ...state,
        bots,
      };

    case SET_ACTIVE_BOT:
      return {
        ...state,
        active: action.payload,
      };

    default:
      return state;
  }
}

const rootReducer = combineReducers({
  form: reduxFormReducer,
  account,
  bot,
  routing,
});

export default rootReducer;
