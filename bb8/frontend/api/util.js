import 'whatwg-fetch';
import store from 'store2';
import AUTH_TOKEN from '../constants';

export default function (method, path, body) {
  const headers = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  };
  if (store.has(AUTH_TOKEN)) {
    headers.Authorization = `Bearer ${store.get(AUTH_TOKEN)}`;
  }

  return fetch(path, {
    method,
    headers,
    body: JSON.stringify(body),
  });
}
