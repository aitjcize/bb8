import { normalize, arrayOf } from 'normalizr'

import fetch from './util'
import { Bot } from '../constants/Schema'

const bot = {
  getAllBots() {
    return fetch('GET', '/api/bots', {})
      .then(response => ({
        response: normalize(response.bots, arrayOf(Bot)),
      }))
      .catch(error => ({ error }))
  },

  getBot(botId) {
    return fetch('GET', `/api/bots/${botId}`, {})
      .then(response => ({ response: normalize(response, Bot) }))
      .catch(error => ({ error }))
  },

  createBot(botObj) {
    return fetch('POST', '/api/bots', botObj)
      .then(response => ({ response: normalize(response, Bot) }))
      .catch(error => ({ error }))
  },

  updateBot(botId, botObj) {
    return fetch('PATCH', `/api/bots/${botId}`, botObj, false)
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },

  deleteBot(botId) {
    return fetch(
        'DELETE',
        `/api/bots/${botId}`, {})
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },
}

export default bot
