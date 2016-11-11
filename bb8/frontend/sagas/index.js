import storage from 'store2'
import { take, call, put, fork } from 'redux-saga/effects'
import { hashHistory } from 'react-router'
import types from '../constants/ActionTypes'
import api from '../api'
import { AUTH_TOKEN } from '../constants'

/* General Saga */

export function* initializeAppSaga() {
  while (true) {
    yield take(types.INITIALIZE_APP)

    yield put({ type: types.BOTS_LIST.REQUEST })
  }
}

/* Authorization Sagas */

export function* logoutSaga() {
  while (true) {
    yield take(types.ACCOUNTS_LOGOUT)
    storage.remove(AUTH_TOKEN)
    hashHistory.push('/login')
  }
}

export function* loginSaga() {
  while (true) {
    const request = yield take(types.ACCOUNTS_LOGIN.REQUEST)
    const { email, passwd } = request.payload

    const { response, error } =
      yield call(api.login, email, passwd)

    if (error) {
      yield put({ type: types.ACCOUNTS_LOGIN.ERROR, payload: error })
      hashHistory.push('/login')
    } else {
      storage.set(AUTH_TOKEN, response.authToken)
      yield put({ type: types.ACCOUNTS_LOGIN.SUCCESS, payload: response })
      hashHistory.push('/')
    }
  }
}

/* Bots Sagas */

export function* fetchBotsSaga() {
  while (true) {
    yield take(types.BOTS_LIST.REQUEST)

    const { response, error } = yield call(api.getAllBots)

    if (error) {
      yield put({ type: types.BOTS_LIST.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_LIST.SUCCESS, payload: response })
    }
  }
}

/* Platform Sagas */

export function* fetchPlatformsSaga() {
  while (true) {
    yield take(types.PLATFORMS_LIST.REQUEST)

    const { response, error } = yield call(api.getPlatforms)

    if (error) {
      yield put({ type: types.PLATFORMS_LIST.ERROR, payload: error })
    } else {
      yield put({ type: types.PLATFORMS_LIST.SUCCESS, payload: response })
    }
  }
}

export function* createPlatformSaga() {
  while (true) {
    const { payload } = yield take(types.PLATFORMS_CREATE.REQUEST)

    const { response, error } = yield call(api.createPlatform, payload)

    if (error) {
      yield put({ type: types.PLATFORMS_CREATE.ERROR, payload: error })
    } else {
      yield put({
        type: types.PLATFORMS_CREATE.SUCCESS,
        payload: response,
      })
    }
  }
}

export function* updatePlatformSaga() {
  while (true) {
    const { payload: { platformId, platform } } = yield take(types.PLATFORMS_UPDATE.REQUEST)

    const { response, error } = yield call(api.updatePlatform, platformId, platform)

    if (error) {
      yield put({ type: types.PLATFORMS_UPDATE.ERROR, payload: error })
    } else {
      yield put({
        type: types.PLATFORMS_UPDATE.SUCCESS,
        payload: response,
      })
    }
  }
}

export function* deletePlatformSaga() {
  while (true) {
    const { payload } = yield take(types.PLATFORMS_DELETE.REQUEST)
    const platformId = payload

    const { error } = yield call(api.deletePlatform, platformId)

    if (error) {
      yield put({ type: types.PLATFORMS_DELETE.ERROR, payload: error })
    } else {
      yield put({ type: types.PLATFORMS_DELETE.SUCCESS, payload: platformId })
    }
  }
}

/* Broadcast Sagas */

export function* fetchBroadcastsSaga() {
  while (true) {
    const { payload } = yield take(types.BROADCASTS_LIST.REQUEST)

    const { response, error } = yield call(api.getAllBroadcasts, payload)

    if (error) {
      yield put({ type: types.BROADCASTS_LIST.ERROR, payload: error })
    } else {
      yield put({
        type: types.BROADCASTS_LIST.SUCCESS,
        payload: response,
      })
    }
  }
}

export function* createBroadcastSaga() {
  while (true) {
    const { payload } = yield take(types.BROADCASTS_CREATE.REQUEST)

    const { response, error } = yield call(api.createBroadcast, payload)
    if (error) {
      yield put({ type: types.BROADCASTS_CREATE.ERROR, payload: error })
    } else {
      yield put({
        type: types.BROADCASTS_CREATE.SUCCESS,
        payload: response,
      })
    }
  }
}

export function* updateBroadcastSaga() {
  while (true) {
    const { payload: { broadcastId, broadcast } }
      = yield take(types.BROADCASTS_UPDATE.REQUEST)

    const { response, error } = yield call(api.updateBroadcast, broadcastId, broadcast)

    if (error) {
      yield put({ type: types.BROADCASTS_UPDATE.ERROR, payload: error })
    } else {
      yield put({
        type: types.BROADCASTS_UPDATE.SUCCESS,
        payload: response,
      })
    }
  }
}

export function* deleteBroadcastSaga() {
  while (true) {
    const { payload } = yield take(types.BROADCASTS_DELETE.REQUEST)
    const broadcastId = payload

    const { error } =
      yield call(api.deleteBroadcast, broadcastId)

    if (error) {
      yield put({ type: types.BROADCASTS_DELETE.ERROR, payload: error })
    } else {
      yield put({
        type: types.BROADCASTS_DELETE.SUCCESS,
        payload: broadcastId,
      })
    }
  }
}

export default function* root() {
  /* General Saga */
  yield fork(initializeAppSaga)

  /* Authorization Saga */
  yield fork(loginSaga)
  yield fork(logoutSaga)

  /* Bots Saga */
  yield fork(fetchBotsSaga)

  /* Platform Saga */
  yield fork(fetchPlatformsSaga)
  yield fork(createPlatformSaga)
  yield fork(updatePlatformSaga)
  yield fork(deletePlatformSaga)

  /* Broadcast Sagas */
  yield fork(fetchBroadcastsSaga)
  yield fork(createBroadcastSaga)
  yield fork(updateBroadcastSaga)
  yield fork(deleteBroadcastSaga)
}
