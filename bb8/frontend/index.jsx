import 'babel-polyfill'
import 'react-lumberjack'

import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { IndexRoute, Router, Route, hashHistory } from 'react-router'
import { syncHistoryWithStore } from 'react-router-redux'
import { createStore, applyMiddleware } from 'redux'
import createSagaMiddleware from 'redux-saga'
import injectTapEventPlugin from 'react-tap-event-plugin'
import createLogger from 'redux-logger'
import storage from 'store2'

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider'
import getMuiTheme from 'material-ui/styles/getMuiTheme'

import { AUTH_TOKEN } from './constants'
import rootSaga from './sagas'
import rootReducer from './reducers'

import initialState from './initialState'

import modules from './modules'
import './styles/style.scss'

const {
  Analytics,
  App,
  Broadcast,
  Dashboard,
  Flow,
  Help,
  Login,
  Platforms,
  Signup,
} = modules

// Needed for onTouchTap (material-ui)
// http://stackoverflow.com/a/34015469/988941
injectTapEventPlugin()

// Configure middleware and store
const logger = createLogger()

const sagaMiddleware = createSagaMiddleware()
const store = createStore(
  rootReducer,
  initialState,
  applyMiddleware(sagaMiddleware, logger),
)
sagaMiddleware.run(rootSaga)

syncHistoryWithStore(hashHistory, store)

const THEME = {
  palette: {
    primary1Color: '#3AD8BD',
    accent1Color: '#FFBA48',
  },
}

const muiTheme = getMuiTheme(THEME)
muiTheme.toolbar.backgroundColor = muiTheme.appBar.color


function authRequired(nextState, replace) {
  if (!storage.has(AUTH_TOKEN)) {
    storage.clearAll()
    replace('/login')
  }
}

function notAuthRequired(nextState, replace) {
  if (storage.has(AUTH_TOKEN)) {
    replace('/')
  }
}

render(
(<Provider store={store}>
  <MuiThemeProvider muiTheme={muiTheme}>
    <Router history={hashHistory}>
      <Route onEnter={authRequired} path="/" component={App} >
        <IndexRoute component={Dashboard} />
        <Route path="dashboard" component={Dashboard} />
        <Route path="flow" component={Flow} />
        <Route path="broadcast" component={Broadcast} />
        <Route path="platforms" component={Platforms} />
        <Route path="analytics" component={Analytics} />
        <Route path="help" component={Help} />
      </Route>
      <Route onEnter={notAuthRequired} path="login" component={Login} />
      <Route onEnter={notAuthRequired} path="signup" component={Signup} />
    </Router>
  </MuiThemeProvider>
</Provider>), document.getElementById('root'))
