import { normalize } from 'normalizr'

import fetch from './util'
import { Platform } from '../constants/Schema'

function normPlatform(platform) {
  return normalize(platform, Platform)
}

const platforms = {
  getPlatforms() {
    return fetch('GET', '/api/platforms', {})
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },

  createPlatform(platform) {
    return fetch('POST', '/api/platforms', platform)
      .then(response => ({ response: normPlatform(response) }))
      .catch(error => ({ error }))
  },

  getPlatform(platformId) {
    return fetch('GET', `/api/platforms/${platformId}`, {})
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },

  updatePlatform(platformId, platform) {
    return fetch('PUT', `/api/platforms/${platformId}`, platform)
      .then(response => ({ response: normPlatform(response) }))
      .catch(error => ({ error }))
  },

  deletePlatform(platformId) {
    return fetch(
        'DELETE',
        `/api/platforms/${platformId}`, {})
      .then(response => ({ response }))
      .catch(error => ({ error }))
  },
}

export default platforms
