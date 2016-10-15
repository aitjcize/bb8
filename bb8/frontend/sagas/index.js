import storage from 'store2';
import { take, call, put, fork } from 'redux-saga/effects';
import { hashHistory } from 'react-router';
import { LOGIN, LOGOUT, FETCH_BOTS } from '../actions';
import api from '../api';
import AUTH_TOKEN from '../constants';

export function* logoutSaga() {
  while (true) {
    yield take(LOGOUT);
    storage.remove(AUTH_TOKEN);
    hashHistory.push('/login');
  }
}

export function* loginSaga() {
  while (true) {
    const request = yield take(LOGIN.REQUEST);
    const { username, passwd } = request.payload;

    const { response, error } =
      yield call(api.login, { username, passwd });

    if (error) {
      yield put({ type: LOGIN.ERROR });
      hashHistory.push('/login');
    } else {
      storage.set(AUTH_TOKEN, response.auth_token);
      yield put({ type: LOGIN.SUCCESS, payload: response });
      hashHistory.push('/login');
    }
  }
}

export function* fetchBots() {
  while (true) {
    yield take(FETCH_BOTS.REQUEST);

    const { error } = yield call(api.fetchAll);

    if (error) {
      yield put({});
    }
  }
}

export default function* root() {
  yield fork(loginSaga);
  yield fork(logoutSaga);
  yield fork(fetchBots);
}
