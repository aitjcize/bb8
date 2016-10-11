import { routerReducer as routing } from 'react-router-redux';
import { combineReducers } from 'redux';

const entities = () => (
  {}
);

const rootReducer = combineReducers({
  entities,
  routing,
});

export default rootReducer;
