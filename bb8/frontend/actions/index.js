import types from '../constants/ActionTypes'

const startLogin = (email, passwd) => ({
  type: types.ACCOUNTS_LOGIN.REQUEST,
  payload: {
    email,
    passwd,
  },
})

const setActiveBot = botId => ({
  type: types.BOTS_SET_ACTIVE,
  payload: botId,
})

export default {
  startLogin,
  setActiveBot,
}
