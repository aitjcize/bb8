import async from 'async'
import omit from 'lodash/omit'
import storage from 'store2'
import { camelizeKeys } from 'humps'
import { hashHistory } from 'react-router'
import { normalize, arrayOf } from 'normalizr'
import { take, call, put, fork } from 'redux-saga/effects'

import api from '../api'
import { FBPage } from '../constants/Schema'
import types from '../constants/ActionTypes'
import { AUTH_TOKEN } from '../constants'
import CustomError from '../constants/CustomError'
import * as broadcastActionCreators from '../actions/broadcastActionCreators'
import * as uiActionCreators from '../actions/uiActionCreators'

/* General Saga */

export function* initializeAppSaga() {
  while (true) {
    yield take(types.INITIALIZE_APP)

    yield put({ type: types.BOTS_LIST.REQUEST })
  }
}

export function* facebookPagesSaga() {
  const iteratee = (item, callback) => {
    // eslint-disable-next-line no-undef
    FB.api(item, (resp) => {
      callback(null, resp)
    })
  }

  const refreshPage = () =>
    new Promise((resolve) => {
      // eslint-disable-next-line no-undef
      FB.login(() => {
        // eslint-disable-next-line no-undef
        FB.api('/me/accounts', (resp) => {
          const paths = resp.data.map(r =>
            `/${r.id}?fields=about,picture,name`)

          async.map(paths, iteratee, (err, results) => {
            const pages = resp.data.map(
              (d, idx) => camelizeKeys(omit(Object.assign(d, {
                ...results[idx], pageId: d.id, id: idx,
              }), ['perms', 'category'])))

            resolve(pages)
          })
        })
      }, { scope: 'manage_pages' })
    })

  while (true) {
    yield take(types.FB_REFRESH_PAGES.REQUEST)

    const pages = yield call(refreshPage)
    yield put({
      type: types.FB_REFRESH_PAGES.SUCCESS,
      payload: normalize(pages, arrayOf(FBPage)),
    })
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

export function* signupSaga() {
  while (true) {
    const request = yield take(types.ACCOUNTS_SIGNUP.REQUEST)
    const { email, passwd, timezone } = request.payload

    const { response, error } = yield call(api.signup, email, passwd, timezone)
    if (error) {
      yield put({ type: types.ACCOUNTS_SIGNUP.ERROR, payload: error })
      hashHistory.push('/signup')
    } else {
      storage.set(AUTH_TOKEN, response.authToken)
      yield put({ type: types.ACCOUNTS_SIGNUP.SUCCESS, payload: response })
      hashHistory.push('/')
    }
  }
}

/* Bots Sagas */

export function* setActiveBotSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_SET_ACTIVE)

    // trigger refresh for current page
    yield put({ type: types.BROADCASTS_LIST.REQUEST, payload })
  }
}

export function* getAllBotsSaga() {
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

export function* createBotSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_CREATE.REQUEST)

    const { response, error } = yield call(api.createBot, payload)

    if (error) {
      yield put({ type: types.BOTS_CREATE.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_CREATE.SUCCESS, payload: response })
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

    if (error && error.body) {
      yield put({ type: types.NOTIFICATION_OPEN, payload: error.body.message })
    }

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

    if (error && error.body.errorCode === CustomError.errDuplicateEntry) {
      yield put({ type: types.NOTIFICATION_OPEN, payload: 'This provider id is already in used' })
    }

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
      yield put(broadcastActionCreators.closeBroadcastEditor())
      yield put(uiActionCreators.openNotification(
        'Failed to create broadcast'))
    } else {
      yield put({
        type: types.BROADCASTS_CREATE.SUCCESS,
        payload: response,
      })
      yield put(broadcastActionCreators.closeBroadcastEditor())
      yield put(uiActionCreators.openNotification(
        'Successfully create a broadcast'))
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
      yield put(broadcastActionCreators.closeBroadcastEditor())
      yield put(uiActionCreators.openNotification(
        'Failed to update the broadcast'))
    } else {
      yield put({
        type: types.BROADCASTS_UPDATE.SUCCESS,
        payload: response,
      })
      yield put(broadcastActionCreators.closeBroadcastEditor())
      yield put(uiActionCreators.openNotification(
        'Successfully update the broadcast'))
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

/* Dialog Saga */

export function* confirmBroadcastDateSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_BROADCAST_DATE.CONFIRM)

    yield put({
      type: types.BROADCASTS_UPDATE.REQUEST,
      payload: {
        broadcastId: payload.id,
        broadcast: Object.assign({}, payload, { status: 'Queued' }),
      },
    })

    yield take(types.BROADCASTS_UPDATE.SUCCESS)
    yield put({ type: types.DIALOG_CLOSE })
  }
}

export function* confirmSendBroadcastSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_BROADCAST_SEND.CONFIRM)

    if (payload.id) {
      yield put({
        type: types.BROADCASTS_UPDATE.REQUEST,
        payload: {
          broadcastId: payload.id,
          broadcast: Object.assign(
            {}, payload, { status: 'Queued', scheduledTime: 0 }),
        },
      })
      yield take(types.BROADCASTS_UPDATE.SUCCESS)
    } else {
      yield put({
        type: types.BROADCASTS_CREATE.REQUEST,
        payload,
      })
      yield take(types.BROADCASTS_CREATE.SUCCESS)
    }

    yield put({ type: types.DIALOG_CLOSE })
    yield put({ type: types.BROADCAST_EDITOR_CLOSE })
  }
}

export function* confirmDelBroadcastSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_BROADCAST_DEL.CONFIRM)

    yield put({
      type: types.BROADCASTS_DELETE.REQUEST,
      payload,
    })

    yield take(types.BROADCASTS_DELETE.SUCCESS)
    yield put({ type: types.DIALOG_CLOSE })
  }
}

export function* confirmDelPlatformSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_PLATFORM_DEL.CONFIRM)

    yield put({
      type: types.PLATFORMS_DELETE.REQUEST,
      payload,
    })

    yield take(types.PLATFORMS_DELETE.SUCCESS)
    yield put({ type: types.DIALOG_CLOSE })
  }
}

export function* confirmCreatePlatformSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_PLATFORM_CREATE.CONFIRM)

    yield put({
      type: types.PLATFORMS_CREATE.REQUEST,
      payload,
    })

    yield take(types.PLATFORMS_CREATE.SUCCESS)
    yield put({ type: types.DIALOG_CLOSE })
  }
}

export function* confirmUpdatePlatformSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_PLATFORM_UPDATE.CONFIRM)

    yield put({
      type: types.PLATFORMS_UPDATE.REQUEST,
      payload: {
        platformId: payload.id,
        platform: payload,
      },
    })

    yield take(types.PLATFORMS_UPDATE.SUCCESS)
    yield put({ type: types.DIALOG_CLOSE })
  }
}

export default function* root() {
  /* General Saga */
  yield fork(initializeAppSaga)

  /* Facebook Saga */
  yield fork(facebookPagesSaga)

  /* Authorization Saga */
  yield fork(loginSaga)
  yield fork(signupSaga)
  yield fork(logoutSaga)

  /* Bots Saga */
  yield fork(setActiveBotSaga)
  yield fork(getAllBotsSaga)
  yield fork(createBotSaga)

  /* Platform Saga */
  yield fork(fetchPlatformsSaga)
  yield fork(createPlatformSaga)
  yield fork(updatePlatformSaga)
  yield fork(deletePlatformSaga)

  /* Broadcast Saga */
  yield fork(fetchBroadcastsSaga)
  yield fork(createBroadcastSaga)
  yield fork(updateBroadcastSaga)
  yield fork(deleteBroadcastSaga)

  /* Dialog Saga */
  yield fork(confirmBroadcastDateSaga)
  yield fork(confirmSendBroadcastSaga)
  yield fork(confirmDelBroadcastSaga)
  yield fork(confirmDelPlatformSaga)
  yield fork(confirmCreatePlatformSaga)
  yield fork(confirmUpdatePlatformSaga)
}
