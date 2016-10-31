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

export const Bot = new Schema('bots', BotRecord, { idAttribute: 'id' })
export const Platform = new Schema('platforms', PlatformRecord, {
  idAttribute: 'id',
})

export default Bot
