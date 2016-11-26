import { normalize, arrayOf } from 'normalizr'

import fetch from './util'
import { Platform } from '../constants/Schema'

const platforms = {
  getPlatforms() {
    return fetch('GET', '/api/platforms', {})
      .then(response => ({
        response: normalize(response.platforms, arrayOf(Platform)),
      }))
      .catch(error => ({ error }))
  },

  getPlatform(platformId) {
    return fetch('GET', `/api/platforms/${platformId}`, {})
      .then(response => ({ response: normalize(response, Platform) }))
      .catch(error => ({ error }))
  },

  createPlatform(platform) {
    return fetch('POST', '/api/platforms', { ...platform, deployed: true })
      .then(response => ({ response: normalize(response, Platform) }))
      .catch(error => ({ error }))
  },

  updatePlatform(platformId, platform) {
    return fetch('PUT', `/api/platforms/${platformId}`, { ...platform, deployed: true })
      .then(() => ({ response: normalize({ ...platform, id: platformId }, Platform) }))
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
