import createRequestTypes from './utils'

export default {
  // Accounts
  ACCOUNTS_REGISTER: createRequestTypes('ACCOUNTS_REGISTER'),
  ACCOUNTS_LOGIN: createRequestTypes('ACCOUNTS_LOGIN'),
  ACCOUNTS_LOGOUT: 'ACCOUNTS_LOGOUT',
  ACCOUNTS_ME: createRequestTypes('ACCOUNTS_ME'),
  ACCOUNTS_VERIFY_EMAIL: createRequestTypes('ACCOUNTS_VERIFY_EMAIL'),

  // Bots
  BOTS_LIST: createRequestTypes('BOTS_LIST'),
  BOTS_GET: createRequestTypes('BOTS_GET'),
  BOTS_CREATE: createRequestTypes('BOTS_CREATE'),
  BOTS_UPDATE: createRequestTypes('BOTS_UPDATE'),
  BOTS_DEPLOY: createRequestTypes('BOTS_DEPLOY'),
  BOTS_DELETE: createRequestTypes('BOTS_DELETE'),

  // Broadcasts
  BROADCASTS_LIST: createRequestTypes('BROADCASTS_LIST'),
  BROADCASTS_GET: createRequestTypes('BROADCASTS_GET'),
  BROADCASTS_CREATE: createRequestTypes('BROADCASTS_CREATE'),
  BROADCASTS_UPDATE: createRequestTypes('BROADCASTS_UPDATE'),
  BROADCASTS_DELETE: createRequestTypes('BROADCASTS_DELETE'),

  // Platforms
  PLATFORMS_LIST: createRequestTypes('PLATFORMS_LIST'),
  PLATFORMS_GET: createRequestTypes('PLATFORMS_GET'),
  PLATFORMS_CREATE: createRequestTypes('PLATFORMS_CREATE'),
  PLATFORMS_UPDATE: createRequestTypes('PLATFORMS_UPDATE'),
  PLATFORMS_DELETE: createRequestTypes('PLATFORMS_DELETE'),
}
