import { camelizeKeys } from 'humps'
import omit from 'lodash/omit'
import async from 'async'

export const authorize = () =>
  new Promise((resolve, reject) => {
    // eslint-disable-next-line no-undef
    FB.getLoginStatus((resp) => {
      if (resp.status === 'connected') {
        resolve({ authResponse: resp.authResponse })
        return
      }
      // eslint-disable-next-line no-undef
      FB.login((response) => {
        if (response.status === 'connected') {
          resolve({ authResponse: response.authResponse })
          return
        }
        reject({ error: new Error('Cannot authorize via Facebook') })
      }, { scope: 'public_profile,email,manage_pages' })
    })
  })

export const fetchMe = () => authorize()
  .then(() =>
    new Promise((resolve) => {
      // eslint-disable-next-line no-undef
      FB.api('/me?fields=name,email', resp => resolve(resp))
    })
  )

export const refreshPage = () => {
  const iteratee = (item, callback) => {
    // eslint-disable-next-line no-undef
    FB.api(item, (resp) => {
      callback(null, resp)
    })
  }
  return authorize()
    .then(() => new Promise((resolve, reject) => {
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
      })
    }))
}
