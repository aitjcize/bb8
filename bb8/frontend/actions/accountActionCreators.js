import types from '../constants/ActionTypes'

// eslint-disable-next-line import/prefer-default-export
export const startLogin = (email, passwd) => ({
  type: types.ACCOUNTS_LOGIN.REQUEST,
  payload: {
    email,
    passwd,
  },
})
