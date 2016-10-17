import types from '../constants/ActionTypes'

const startLogin = (email, passwd) => ({
  type: types.ACCOUNTS_LOGIN.REQUEST,
  payload: {
    email,
    passwd,
  },
})

export default startLogin
