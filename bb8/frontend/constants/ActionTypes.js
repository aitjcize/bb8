import { createRequestTypes, createDialogTypes } from './utils'

export default {

  // General
  INITIALIZE_APP: 'INITIALIZE_APP',

  // Accounts
  ACCOUNTS_REGISTER: createRequestTypes('ACCOUNTS_REGISTER'),
  ACCOUNTS_LOGIN: createRequestTypes('ACCOUNTS_LOGIN'),
  ACCOUNTS_LOGOUT: 'ACCOUNTS_LOGOUT',
  ACCOUNTS_GET_ME: createRequestTypes('ACCOUNTS_GET_ME'),
  ACCOUNTS_VERIFY_EMAIL: createRequestTypes('ACCOUNTS_VERIFY_EMAIL'),

  // Bots
  BOTS_LIST: createRequestTypes('BOTS_LIST'),
  BOTS_GET: createRequestTypes('BOTS_GET'),
  BOTS_CREATE: createRequestTypes('BOTS_CREATE'),
  BOTS_UPDATE: createRequestTypes('BOTS_UPDATE'),
  BOTS_DEPLOY: createRequestTypes('BOTS_DEPLOY'),
  BOTS_DELETE: createRequestTypes('BOTS_DELETE'),
  BOTS_SET_ACTIVE: 'BOTS_SET_ACTIVE',

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

  // UI
  NOTIFICATION_OPEN: 'NOTIFICATION_OPEN',
  NOTIFICATION_CLOSE: 'NOTIFICATION_CLOSE',

  // Dialog
  DIALOG_CLOSE: 'DIALOG_CLOSE',
  DIALOG_BROADCAST_DATE: createDialogTypes('DIALOG_BROADCAST_DATE'),
  DIALOG_BROADCAST_SEND: createDialogTypes('DIALOG_BROADCAST_SEND'),
  DIALOG_BROADCAST_DEL: createDialogTypes('DIALOG_BROADCAST_DEL'),
}
