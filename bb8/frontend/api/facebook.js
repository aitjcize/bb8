import 'isomorphic-fetch'
import omit from 'lodash/omit'
import async from 'async'
import storage from 'store2'
import { camelizeKeys } from 'humps'
import { ACCESS_TOKEN } from '../constants'

export const authorize = () =>
  new Promise((resolve, reject) => {
    const headers = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    }

    if (storage.has(ACCESS_TOKEN)) {
      fetch('/api/facebook_token_check', {
        headers,
        method: 'POST',
        body: JSON.stringify({ accessToken: storage.get(ACCESS_TOKEN) }),
      }).then((response) => {
        if (response.ok) {
          resolve({ accessToken: storage.get(ACCESS_TOKEN) })
          return
        }
        reject({ error: new Error('Cannot verify token') })
      })
      return
    }

    // eslint-disable-next-line no-undef
    FB.login((response) => {
      if (response.status === 'connected') {
        // Get long-lived access token
        fetch('/api/facebook_token_extend', {
          headers,
          method: 'POST',
          body: JSON.stringify(
              { accessToken: response.authResponse.accessToken }),
        }).then((response2) => {
          if (response2.ok) {
            response2.json().then((json) => {
              storage.set(ACCESS_TOKEN, json.accessToken)
              resolve(json)
              return
            })
            return
          }
          reject({ error: new Error('Cannot exchange token') })
        })
        return
      }
      reject({ error: new Error('Cannot authorize via Facebook') })
    }, { scope: 'public_profile,email,manage_pages,pages_messaging' })
  })

export const fetchMe = () => authorize()
  .then(response =>
    new Promise((resolve) => {
      // eslint-disable-next-line no-undef
      FB.api('/me?fields=name,email', resp => resolve(resp))
    },
    { access_token: response.accessToken })
  )

export const subscribeApp = (pageToken, subscribe) =>
  fetch(`https://graph.facebook.com/v2.8/me/subscribed_apps?access_token=${pageToken}`, {
    method: subscribe ? 'POST' : 'DELETE',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
  })
  .then(resp => resp.json())
  .catch(error => Promise.reject(error))

export const refreshPage = () => authorize()
  .then(response => new Promise((resolve, reject) => {
    const iteratee = (item, callback) => {
      // eslint-disable-next-line no-undef
      FB.api(item, (resp) => {
        callback(null, resp)
      },
      { access_token: response.accessToken })
    }
    // eslint-disable-next-line no-undef
    FB.api('/me/accounts', (resp) => {
      const paths = resp.data.map(r =>
        `/${r.id}?fields=about,picture,name`)

      async.map(paths, iteratee, (err, results) => {
        if (err) return reject(err)

        const pages = resp.data.map(
          (d, idx) => camelizeKeys(omit(Object.assign(d, {
            ...results[idx], pageId: d.id, id: idx,
          }), ['perms', 'category'])))

        return resolve(pages)
      })
    },
    { access_token: response.accessToken })
  }))
