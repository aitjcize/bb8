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
    return fetch('PATCH', `/api/bots/${botId}`, botObj)
      .then(() => ({ response: normalize({ ...botObj.bot, id: botId }, Bot) }))
      .catch(error => ({ error }))
  },

  deleteBot(botId) {
    return fetch(
        'DELETE',
        `/api/bots/${botId}`, {})
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },

  deployBot(botId) {
    return fetch('PUT', `/api/bots/${botId}`, {})
      .then(response => ({
        response: normalize({
          id: botId,
          version: response.version,
        }, Bot),
      }))
      .catch(error => ({ error }))
  },

  listBotDefRevisions(botId) {
    return fetch('GET', `/api/bots/${botId}/revisions`, {})
      .then(response => ({
        response: normalize({
          id: botId,
          botDefs: response.botDefs,
        }, Bot),
      }))
      .catch(error => ({ error }))
  },

  getBotDefRevision(botId, version) {
    return fetch('GET', `/api/bots/${botId}/revisions/${version}`, {})
      .then(response => ({
        response: normalize({
          id: botId,
          botJson: response.botJson,
        }, Bot),
      }))
      .catch(error => ({ error }))
  },
}

export default bot
