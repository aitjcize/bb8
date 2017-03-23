import 'babel-polyfill'

import React from 'react'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { IndexRoute, Router, Route, hashHistory } from 'react-router'
import { syncHistoryWithStore } from 'react-router-redux'
import injectTapEventPlugin from 'react-tap-event-plugin'
import storage from 'store2'

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider'
import muiTheme from './constants/Theme'
import { AUTH_TOKEN } from './constants'

import reduxStore from './reduxStore'

import modules from './modules'
import './styles/style.scss'

const {
  Analytics,
  App,
  Login,
  BotManager,
  Signup,
} = modules

// Needed for onTouchTap (material-ui)
// http://stackoverflow.com/a/34015469/988941
injectTapEventPlugin()

syncHistoryWithStore(hashHistory, reduxStore)

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
(<Provider store={reduxStore}>
  <MuiThemeProvider muiTheme={muiTheme}>
    <Router history={hashHistory}>
      <Route onEnter={authRequired} path="/" component={App} >
        <IndexRoute component={BotManager} />
        <Route path="botmanager" component={BotManager} />
        <Route path="analytics" component={Analytics} />
      </Route>
      <Route onEnter={notAuthRequired} path="login" component={Login} />
      <Route onEnter={notAuthRequired} path="signup" component={Signup} />
    </Router>
  </MuiThemeProvider>
</Provider>), document.getElementById('root'))
