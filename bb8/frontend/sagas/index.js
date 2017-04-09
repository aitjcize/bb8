import storage from 'store2'
import { hashHistory } from 'react-router'
import { normalize, arrayOf } from 'normalizr'
import { take, call, put, fork } from 'redux-saga/effects'

import api from '../api'
import { FBPage } from '../constants/Schema'
import types from '../constants/ActionTypes'
import { AUTH_TOKEN, ACTIVE_BOT } from '../constants'
import CustomError from '../constants/CustomError'
import * as broadcastActionCreators from '../actions/broadcastActionCreators'
import * as uiActionCreators from '../actions/uiActionCreators'
import * as fbAPI from '../api/facebook'

/* General Saga */

export function* initializeAppSaga() {
  while (true) {
    yield take(types.INITIALIZE_APP)

    yield put({ type: types.BOTS_LIST.REQUEST })
  }
}

export function* facebookPagesSaga() {
  while (true) {
    yield take(types.FB_REFRESH_PAGES.REQUEST)

    const pages = yield call(fbAPI.refreshPage)

    yield put({
      type: types.FB_REFRESH_PAGES.SUCCESS,
      payload: normalize(pages, arrayOf(FBPage)),
    })
  }
}

/* Authorization Sagas */

export function* facebookAuthSaga() {
  while (true) {
    const request = yield take(types.FACEBOOK_AUTH.REQUEST)
    const { inviteCode } = request.payload

    const { accessToken, error } = yield call(fbAPI.authorize)

    if (error) {
      yield put(uiActionCreators.openNotification(
        'Failed to authorize with Facebook, please try again later'))
      yield put({ type: types.FACEBOOK_AUTH.ERROR, payload: error })
      // eslint-disable-next-line no-continue
      continue
    }
    const { email } = yield call(fbAPI.fetchMe)
    const resp = yield call(api.social_auth, email, 'Facebook',
        accessToken, inviteCode)

    if (resp.error) {
      yield put(uiActionCreators.openNotification(
        `Failed to signup: ${resp.error}`))
      yield put({ type: types.FACEBOOK_AUTH.ERROR, payload: resp.error })
      storage.clear()
      // eslint-disable-next-line no-continue
      continue
    }
    storage.set(AUTH_TOKEN, resp.response.authToken)
    yield put({ type: types.FACEBOOK_AUTH.ERROR, payload: resp.response })
    hashHistory.push('/')
  }
}

export function* logoutSaga() {
  while (true) {
    yield take(types.ACCOUNTS_LOGOUT)
    storage.clear()
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

export function* inviteSaga() {
  while (true) {
    const { payload } = yield take(types.ACCOUNTS_INVITE.REQUEST)

    const { inviteCode, error } = yield call(api.invite, payload)

    if (error) {
      yield put({ type: types.ACCOUNTS_INVITE.ERROR, payload: error })
      yield put(uiActionCreators.openNotification(
        'Failed to invite this email'))
    } else {
      yield put({ type: types.ACCOUNTS_INVITE.SUCCESS, payload: inviteCode })
    }
  }
}

/* Bots Sagas */

export function* setActiveBotSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_SET_ACTIVE)

    storage.set(ACTIVE_BOT, payload)

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

export function* updateBotSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_UPDATE.REQUEST)

    const { response, error } = yield call(api.updateBot, payload.botId, payload.botObj)

    if (error) {
      yield put({ type: types.BOTS_UPDATE.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_UPDATE.SUCCESS, payload: response })
    }
  }
}

export function* deployBotSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_DEPLOY.REQUEST)

    const { response, error } = yield call(api.deployBot, payload)

    if (error) {
      yield put({ type: types.BOTS_DEPLOY.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_DEPLOY.SUCCESS, payload: response })
    }
  }
}

export function* deleteBotSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_DELETE.REQUEST)
    const botId = payload

    const { error } = yield call(api.deleteBot, botId)

    if (error) {
      yield put({ type: types.BOTS_DELETE.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_DELETE.SUCCESS, payload: botId })
    }
  }
}

export function* updateBotDefRevisionsSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_UPDATE_DEFS.REQUEST)

    const { response, error } = yield call(api.updateBotDefRevisions, payload.botId, payload.botDef)

    if (error) {
      yield put({ type: types.BOTS_UPDATE_DEFS.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_UPDATE_DEFS.SUCCESS, payload: response })
      yield put({ type: types.BOTS_DEPLOY.REQUEST, payload: payload.botId })
    }
  }
}

export function* listBotDefRevisionsSaga() {
  while (true) {
    const { payload } = yield take(types.BOTS_LIST_DEF_REVISIONS.REQUEST)

    const { response, error } = yield call(api.listBotDefRevisions, payload)

    if (error) {
      yield put({ type: types.BOTS_LIST_DEF_REVISIONS.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_LIST_DEF_REVISIONS.SUCCESS, payload: response })
    }
  }
}

export function* getBotDefRevision() {
  while (true) {
    const { payload: { botId, version } } =
      yield take(types.BOTS_GET_DEF_REVISIONS.REQUEST)

    const { response, error } = yield call(api.getBotDefRevision, botId, version)

    if (error) {
      yield put({ type: types.BOTS_GET_DEF_REVISIONS.ERROR, payload: error })
    } else {
      yield put({ type: types.BOTS_GET_DEF_REVISIONS.SUCCESS, payload: response })
    }
  }
}

/* Platform Sagas */

export function* refreshPageSaga() {
  while (true) {
    const { payload } = yield take(types.PLATFORMS_REFRESH.REQUEST)
    const platform = payload

    const page = yield call(fbAPI.getRefreshedPage, platform.providerIdent)
    const { response, error } = yield call(
      api.updatePlatform,
      platform.id,
      Object.assign(
        {}, platform,
        {
          name: page.name,
          config: { accessToken: page.accessToken },
        }))

    if (error) {
      yield put({
        type: types.PLATFORMS_REFRESH.ERROR,
        payload: error,
      })
      yield put({
        type: types.NOTIFICATION_OPEN,
        payload: 'Cannot refresh the page',
      })
    } else {
      yield put({
        type: types.PLATFORMS_REFRESH.SUCCESS,
        payload: response,
      })
      yield put({
        type: types.NOTIFICATION_OPEN,
        payload: 'Successfully refreshed the page',
      })
    }
  }
}

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

    if (platform.typeEnum === 'Facebook') {
      const { error } = yield call(
          fbAPI.subscribeApp, platform.config.accessToken, platform.botId !== null)
      if (error) {
        yield put({ type: types.NOTIFICATION_OPEN, payload: 'Cannot attach bot to your facebook fans page, please try again later' })
        // eslint-disable-next-line no-continue
        continue
      }
    }

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
    const platform = payload

    // Unsubscribe app before deleting the platform.
    if (platform.typeEnum === 'Facebook') {
      yield call(fbAPI.subscribeApp, platform.config.accessToken, false)
    }

    const { error } = yield call(api.deletePlatform, platform.id)

    if (error) {
      yield put({ type: types.PLATFORMS_DELETE.ERROR, payload: error })
    } else {
      yield put({ type: types.PLATFORMS_DELETE.SUCCESS, payload: platform.id })
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

export function* confirmDelBotSaga() {
  while (true) {
    const { payload } = yield take(types.DIALOG_BOT_DELETE.CONFIRM)

    yield put({
      type: types.BOTS_DELETE.REQUEST,
      payload,
    })

    yield take([types.BOTS_DELETE.SUCCESS, types.BOTS_DELETE.ERROR])
    yield put({ type: types.DIALOG_CLOSE })
  }
}

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

    yield take([types.BROADCASTS_UPDATE.SUCCESS, types.BROADCASTS_UPDATE.ERROR])
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
      yield take([types.BROADCASTS_UPDATE.SUCCESS, types.BROADCASTS_UPDATE.ERROR])
    } else {
      yield put({
        type: types.BROADCASTS_CREATE.REQUEST,
        payload,
      })
      yield take([types.BROADCASTS_CREATE.SUCCESS, types.BROADCASTS_CREATE.ERROR])
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

    yield take([types.BROADCASTS_DELETE.SUCCESS, types.BROADCASTS_DELETE.ERROR])
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

    yield take([types.PLATFORMS_DELETE.SUCCESS, types.PLATFORMS_DELETE.ERROR])
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

    yield take([types.PLATFORMS_CREATE.SUCCESS, types.PLATFORMS_CREATE.ERROR])
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

    yield take([types.PLATFORMS_UPDATE.SUCCESS, types.PLATFORMS_UPDATE.ERROR])
    yield put({ type: types.DIALOG_CLOSE })
  }
}

export default function* root() {
  /* General Saga */
  yield fork(initializeAppSaga)

  /* Facebook Saga */
  yield fork(facebookPagesSaga)

  /* Authorization Saga */
  yield fork(facebookAuthSaga)
  yield fork(loginSaga)
  yield fork(signupSaga)
  yield fork(logoutSaga)
  yield fork(inviteSaga)

  /* Bots Saga */
  yield fork(setActiveBotSaga)
  yield fork(getAllBotsSaga)
  yield fork(createBotSaga)
  yield fork(updateBotSaga)
  yield fork(deleteBotSaga)
  yield fork(deployBotSaga)
  yield fork(listBotDefRevisionsSaga)
  yield fork(getBotDefRevision)
  yield fork(updateBotDefRevisionsSaga)

  /* Platform Saga */
  yield fork(refreshPageSaga)
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
  yield fork(confirmDelBotSaga)
  yield fork(confirmCreatePlatformSaga)
  yield fork(confirmUpdatePlatformSaga)
}
