import { createStore, applyMiddleware } from 'redux'
import createSagaMiddleware from 'redux-saga'
import createLogger from 'redux-logger'

import rootSaga from './sagas'
import rootReducer from './reducers'
import initialState from './initialState'

// Configure middleware and store
const logger = createLogger()

const sagaMiddleware = createSagaMiddleware()
const store = createStore(
  rootReducer,
  initialState,
  applyMiddleware(sagaMiddleware, logger),
)
sagaMiddleware.run(rootSaga)

export default store
