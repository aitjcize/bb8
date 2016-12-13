import fetch from './util'

const auth = {
  login(email, passwd) {
    return fetch('POST', '/api/login', {
      email, passwd,
    })
    .then(response => ({ response }))
    .catch(error => ({ error }))
  },
  signup(email, passwd, timezone) {
    return fetch('POST', '/api/email_register', {
      email, passwd, timezone,
    })
    .then(response => ({ response }))
    .catch(error => ({ error }))
  },
  social_auth(email, provider, providerToken) {
    return fetch('POST', '/api/social_auth', {
      email, provider, providerToken,
    })
    .then(response => ({ response }))
    .catch(error => ({ error }))
  },
}

export default auth
