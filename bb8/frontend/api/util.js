import 'whatwg-fetch'
import store from 'store2'
import { camelizeKeys, decamelizeKeys } from 'humps'

import { AUTH_TOKEN } from '../constants'


// make the fetch reject on non 2xx status
function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response
  }
  const error = new Error(response.statusText)
  error.response = response
  throw error
}


export default function (method, path, body) {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  }
  if (store.has(AUTH_TOKEN)) {
    headers['X-COMPOSEAI-AUTH'] = `Bearer ${store.get(AUTH_TOKEN)}`
  }

  const config = {
    method,
    headers,
  }
  if (method === 'POST' || method === 'PUT') {
    config.body = JSON.stringify(decamelizeKeys(body))
  }
  return fetch(path, config)
    .then(checkStatus)
    .then(response => response.json())
    .then(json => camelizeKeys(json))
}
