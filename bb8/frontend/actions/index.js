import createRequestTypes from './utils';

const LOGIN = createRequestTypes('LOGIN');
const LOGOUT = 'LOGOUT';

const startLogin = (email, passwd) => ({
  type: LOGIN.REQUEST,
  payload: {
    email,
    passwd,
  },
});

const BOTS_GET_ALL = createRequestTypes('BOTS_GET_ALL');

export {
  LOGIN,
  LOGOUT,
  BOTS_GET_ALL,

  startLogin,
};
