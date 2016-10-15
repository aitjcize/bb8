import createRequestTypes from './utils';

const LOGIN = createRequestTypes('LOGIN');
const LOGOUT = 'LOGOUT';

const FETCH_BOTS = createRequestTypes('FETCH_BOTS');

export { LOGIN, LOGOUT, FETCH_BOTS };
