import types from '../constants/ActionTypes'

export const startfacebookAuth = () => ({
  type: types.FACEBOOK_AUTH.REQUEST,
})

export const startLogin = (email, passwd) => ({
  type: types.ACCOUNTS_LOGIN.REQUEST,
  payload: {
    email,
    passwd,
  },
})

export const startSignup = (email, passwd, timezone) => ({
  type: types.ACCOUNTS_SIGNUP.REQUEST,
  payload: {
    email, passwd, timezone,
  },
})
