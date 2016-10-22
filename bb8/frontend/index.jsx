import 'babel-polyfill'

import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { IndexRoute, Router, Route, hashHistory } from 'react-router'
import { syncHistoryWithStore } from 'react-router-redux'
import { createStore, applyMiddleware } from 'redux'
import createSagaMiddleware from 'redux-saga'
import injectTapEventPlugin from 'react-tap-event-plugin'
import createLogger from 'redux-logger'

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider'
import getMuiTheme from 'material-ui/styles/getMuiTheme'

import rootSaga from './sagas'
import rootReducer from './reducers'

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
const logger = createLogger({
  stateTransformer(state) {
    return state.toJS()
  },
})
const sagaMiddleware = createSagaMiddleware()
const store = createStore(
    rootReducer,
    applyMiddleware(sagaMiddleware, logger),
)
sagaMiddleware.run(rootSaga)

syncHistoryWithStore(hashHistory, store, {
  selectLocationState(state) {
    return state.get('routing').toJS()
  },
})

const muiTheme = getMuiTheme()
muiTheme.toolbar.backgroundColor = muiTheme.appBar.color

render(
(<Provider store={store}>
  <MuiThemeProvider muiTheme={muiTheme}>
    <Router history={hashHistory}>
      <Route path="/" component={App} >
        <IndexRoute component={Dashboard} />
        <Route path="dashboard" component={Dashboard} />
        <Route path="flow" component={Flow} />
        <Route path="broadcast" component={Broadcast} />
        <Route path="platforms" component={Platforms} />
        <Route path="analytics" component={Analytics} />
        <Route path="help" component={Help} />
      </Route>
      <Route path="login" component={Login} />
      <Route path="signup" component={Signup} />
    </Router>
  </MuiThemeProvider>
</Provider>), document.getElementById('root'))
