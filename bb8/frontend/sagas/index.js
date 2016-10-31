import storage from 'store2'
import { take, call, put, fork } from 'redux-saga/effects'
import { hashHistory } from 'react-router'
import types from '../constants/ActionTypes'
import api from '../api'
import { AUTH_TOKEN } from '../constants'

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
      yield put({ type: types.ACCOUNTS_LOGIN.ERROR })
      hashHistory.push('/login')
    } else {
      storage.set(AUTH_TOKEN, response.authToken)
      yield put({ type: types.ACCOUNTS_LOGIN.SUCCESS, payload: response })
      hashHistory.push('/')
    }
  }
}

export function* fetchBots() {
  while (true) {
    yield take(types.BOTS_LIST.REQUEST)

    const { response, error } = yield call(api.getAllBots)

    if (error) {
      yield put({ type: types.BOTS_LIST.ERROR })
    } else {
      yield put({ type: types.BOTS_LIST.SUCCESS, payload: response.bots })
    }
  }
}

export function* fetchPlatforms() {
  while (true) {
    yield take(types.PLATFORMS_LIST.REQUEST)

    const { response, error } = yield call(api.getPlatforms)

    if (error) {
      yield put({ type: types.PLATFORMS_LIST.ERROR })
    } else {
      yield put({ type: types.PLATFORMS_LIST.SUCCESS, payload: response })
    }
  }
}

export function* createPlatform() {
  while (true) {
    const { payload } = yield take(types.PLATFORMS_CREATE.REQUEST)

    const { response, error } = yield call(api.createPlatform, payload)

    if (error) {
      yield put({ type: types.PLATFORMS_CREATE.ERROR })
    } else {
      yield put({
        type: types.PLATFORMS_CREATE.SUCCESS,
        payload: response,
      })
    }
  }
}

export function* updatePlatform() {
  while (true) {
    const { payload: { platformId, platform } } = yield take(types.PLATFORMS_UPDATE.REQUEST)

    const { response, error } = yield call(api.updatePlatform, platformId, platform)

    if (error) {
      yield put({ type: types.PLATFORMS_UPDATE.ERROR })
    } else {
      yield put({ type: types.PLATFORMS_UPDATE.SUCCESS, payload: response })
    }
  }
}


export function* deletePlatform() {
  while (true) {
    const { payload } = yield take(types.PLATFORMS_DELETE.REQUEST)
    const platformId = payload

    const { error } = yield call(api.deletePlatform, platformId)

    if (error) {
      yield put({ type: types.PLATFORMS_DELETE.ERROR })
    } else {
      yield put({ type: types.PLATFORMS_DELETE.SUCCESS, payload: platformId })
    }
  }
}

export default function* root() {
  yield fork(loginSaga)
  yield fork(logoutSaga)
  yield fork(fetchBots)
  yield fork(fetchPlatforms)
  yield fork(createPlatform)
  yield fork(updatePlatform)
  yield fork(deletePlatform)
}
