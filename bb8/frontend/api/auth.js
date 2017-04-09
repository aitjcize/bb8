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
  social_auth(email, provider, providerToken, inviteCode) {
    return fetch('POST', '/api/social_auth', {
      email, provider, providerToken, inviteCode,
    })
    .then(response => ({ response }))
    .catch(error => ({ error }))
  },
  invite(email) {
    return fetch('POST', '/api/invite_code', {
      email,
    })
    .then(response => ({ inviteCode: response.inviteCode }))
    .catch(error => ({ error }))
  },
}

export default auth
