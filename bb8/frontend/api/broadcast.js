import { normalize, arrayOf } from 'normalizr'

import fetch from './util'
import { Broadcast } from '../constants/Schema'

const broadcast = {
  getAllBroadcasts(botId) {
    return fetch('GET', `/api/bots/${botId}/broadcasts`, {}, true, false)
      .then(response => ({
        response: normalize(response.broadcasts, arrayOf(Broadcast)),
      }))
      .catch(error => ({ error }))
  },

  getBroadcast(broadcastId) {
    return fetch('GET', `/api/broadcasts/${broadcastId}`, {}, true, false)
      .then(response => ({ response: normalize(response, Broadcast) }))
      .catch(error => ({ error }))
  },

  createBroadcast(broadcastObj) {
    return fetch('POST', '/api/broadcasts', broadcastObj)
      .then(response => ({
        response: normalize(
          Object.assign({}, response, { messages: broadcastObj.messages }), Broadcast),
      }))
      .catch(error => ({ error }))
  },

  updateBroadcast(broadcastId, broadcastObj) {
    return fetch('PUT', `/api/broadcasts/${broadcastId}`, broadcastObj)
      .then(() =>
        ({
          response: normalize(Object.assign(broadcastObj, { id: broadcastId }),
                              Broadcast),
        })
      )
      .catch(error => ({ error }))
  },

  deleteBroadcast(broadcastId) {
    return fetch(
        'DELETE',
        `/api/broadcasts/${broadcastId}`, {})
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },
}

export default broadcast
