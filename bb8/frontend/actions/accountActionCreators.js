import types from '../constants/ActionTypes'

export const startfacebookAuth = inviteCode => ({
  type: types.FACEBOOK_AUTH.REQUEST,
  payload: {
    inviteCode,
  },
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

export const logout = () => ({
  type: types.ACCOUNTS_LOGOUT,
  payload: {},
})

export const invite = email => ({
  type: types.ACCOUNTS_INVITE.REQUEST,
  payload: email,
})
