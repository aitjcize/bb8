import storage from 'store2'
import { take, call, put, fork } from 'redux-saga/effects'
import { hashHistory } from 'react-router'
import types from '../constants/ActionTypes'
import api from '../api'
import AUTH_TOKEN from '../constants'

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
      storage.set(AUTH_TOKEN, response.auth_token)
      yield put({ type: types.ACCOUNTS_LOGIN.SUCCESS, payload: response })
      hashHistory.push('/login')
    }
  }
}

export function* fetchBots() {
  while (true) {
    yield take(types.BOTS_LIST.REQUEST)

    const { bots, error } = yield call(api.getAllBots)

    if (error) {
      yield put({ type: types.BOTS_LIST.ERROR })
    } else {
      yield put({ type: types.BOTS_LIST.SUCCESS, payload: bots })
    }
  }
}

export default function* root() {
  yield fork(loginSaga)
  yield fork(logoutSaga)
  yield fork(fetchBots)
}
