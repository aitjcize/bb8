import { Schema } from 'normalizr'

const BotRecord = {
  id: null,
  name: null,
  description: null,
  interactionTimeout: null,
  adminInteractionTimeout: null,
  sessionTimeout: null,
  gaId: null,
  settings: null,
  staging: null,
}

const PlatformRecord = {
  id: null,
  botId: null,
  name: null,
  typeEnum: null,
  providerIdent: null,
  config: null,
}

const BroadcastRecord = {
  id: null,
  name: null,
  scheduledTime: null,
  status: null,
  messages: null,
}

const FBPageRecord = {
  about: null,
  access_token: null,
  name: null,
  pageId: null,
  picture: null,
}

export const Bot = new Schema('bots', BotRecord, { idAttribute: 'id' })

export const Platform = new Schema('platforms', PlatformRecord, {
  idAttribute: 'id',
})

export const Broadcast = new Schema('broadcasts', BroadcastRecord, {
  idAttribute: 'id',
})

export const FBPage = new Schema('fbpages', FBPageRecord, {
  idAttribute: 'id',
})
