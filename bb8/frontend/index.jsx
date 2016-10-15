import 'babel-polyfill';

import React from 'react';
import { render } from 'react-dom';
import { Router, Route, hashHistory } from 'react-router';
import { syncHistoryWithStore } from 'react-router-redux';
import { createStore, applyMiddleware } from 'redux';
import createSagaMiddleware from 'redux-saga';
import injectTapEventPlugin from 'react-tap-event-plugin';

import apiClient from './api';
import App from './modules/App';
import rootSaga from './sagas';
import rootReducer from './reducers';

import './styles/style.scss';

// Needed for onTouchTap (material-ui)
// http://stackoverflow.com/a/34015469/988941
injectTapEventPlugin();

// Configure middleware and store
const sagaMiddleware = createSagaMiddleware();
const store = createStore(
    rootReducer,
    applyMiddleware(sagaMiddleware)
);
sagaMiddleware.run(rootSaga);

// inject for debugging purpose
// FIXME(kevin): remove this
document.apiClient = apiClient;

syncHistoryWithStore(hashHistory, store);

render((<Router history={hashHistory}>
  <Route path="/" component={App} />
  <Route path="/route1" component={App} />
  <Route path="/route2" component={App} />
</Router>), document.getElementById('root'));
