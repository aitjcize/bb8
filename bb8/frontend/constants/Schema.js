import Immutable from 'immutable'
import { Schema } from 'normalizr-immutable'

const BotRecord = new Immutable.Record({
  id: null,
  name: null,
  description: null,
  interaction_timeout: null,
  admin_interaction_timeout: null,
  session_timeout: null,
  ga_id: null,
  settings: null,
  staging: null,
})

const PlatformRecord = new Immutable.Record({
  id: null,
  bot_id: null,
  name: null,
  type_enum: null,
  provider_ident: null,
  config: null
})

export const Bot = new Schema('bots', BotRecord, { idAttribute: 'id' })
export const Platform = new Schema('platforms', PlatformRecord, {
  idAttribute: 'id'
})

export default Bot
