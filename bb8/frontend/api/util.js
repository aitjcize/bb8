import 'isomorphic-fetch'
import store from 'store2'
import { camelizeKeys, decamelizeKeys } from 'humps'

import { AUTH_TOKEN } from '../constants'

// make the fetch reject on non 2xx status
function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response
  }
  return response.json().then((json) => {
    const error = new Error(response.statusText)
    error.response = response
    error.body = camelizeKeys(json)
    throw error
  })
}


export default function (method, path, body, shouldDecamelize = true) {
  const normedPath = process.env.NODE_ENV === 'test' ?
    `http://localhost:${process.env.HTTP_PORT}${path}` : path

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

  if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
    config.body = JSON.stringify(
      shouldDecamelize ? decamelizeKeys(body) : body)
  }
  return fetch(normedPath, config)
    .then(checkStatus)
    .then(response => response.json())
    .then(json => camelizeKeys(json))
}
