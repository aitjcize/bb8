import React from 'react';
import { render } from 'react-dom';
import { Router, Route, hashHistory } from 'react-router';
import { syncHistoryWithStore } from 'react-router-redux';
import injectTapEventPlugin from 'react-tap-event-plugin';
import App from './modules/App';
import configureStore from './store/configureStore';
import './styles/style.scss';

// Needed for onTouchTap (material-ui)
// http://stackoverflow.com/a/34015469/988941
injectTapEventPlugin();

const store = configureStore();
syncHistoryWithStore(hashHistory, store);

render((<Router history={hashHistory}>
  <Route path="/" component={App} />
  <Route path="/route1" component={App} />
  <Route path="/route2" component={App} />
</Router>), document.getElementById('root'));
