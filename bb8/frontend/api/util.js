import 'whatwg-fetch'
import store from 'store2'
import AUTH_TOKEN from '../constants'


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
    headers.Authorization = `Bearer ${store.get(AUTH_TOKEN)}`
  }

  return fetch(path, {
    method,
    headers,
    body: JSON.stringify(body),
  })
  .then(checkStatus)
  .then(response => response.json())
}
