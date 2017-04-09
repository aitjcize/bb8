import { spawn } from 'child_process'
import storage from 'store2'

import api from './index'
import { AUTH_TOKEN } from '../constants'
import { readFileSync } from 'fs'

const PORT = 7002
const DELAY_MSECONDS = 1000

const mockBot = {
  name: 'Bot 1',
  description: 'Bot 1',
}

const mockUpdatedBot =
  JSON.parse(readFileSync('../../bots/test/bot_fmt_test.bot').toString())

const mockPlatform = {
  name: 'platform 1',
  typeEnum: 'Facebook',
  providerIdent: '123',
  deployed: true,
  config: {
    accessToken: '456',
  },
}

const mockBroadcast = {
  botId: 1,
  messages: [{'text': 'Test message'}],
  name: 'broadcast 1',
  scheduledTime: parseInt(Date.now() / 1000),
}

const cmd = spawn('manage', ['runserver', '--no-ssl'])
console.log('turning up server...')

cmd.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`)
})

cmd.stderr.on('data', (data) => {
  console.log(`stderr: ${data}`)
})

function delay(msec) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve()
    }, msec)
  })
}

describe('API testing', () => {

  afterAll(() => {
    spawn('pkill', ['-9', '-f', 'runserver'])
    console.log('turning off server...')
  })

  it('should test the account APIs', () =>
    delay(DELAY_MSECONDS)
      .then(() => api.signup('tester1@gmail.com', '123123', 'Asia/Taipei'))
      .then(() => api.login('tester1@gmail.com', '123123'))
      .then((resp) => {
        expect(resp.response.email).toEqual('tester1@gmail.com')
        expect(resp.response.authToken.length).toBeGreaterThan(20)
        storage.set(AUTH_TOKEN, resp.response.authToken)
        return Promise.resolve()
      })
      .then(() => api.invite('tester2@gmail.com'))
      .then((inviteCode) => {
        expect(inviteCode.length).toBeGreaterThan(10)
      })
      .catch((error) => console.log(error))
  )

  it('should test the bot APIs', () =>
    delay(DELAY_MSECONDS)
      .then(() => api.signup('tester2@gmail.com', '123123', 'Asia/Taipei'))
      .then(() => api.login('tester2@gmail.com', '123123'))
      .then((resp) => { storage.set(AUTH_TOKEN, resp.response.authToken) })
      .then(() => api.createBot(mockBot))
      .then((resp) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities).toEqual('object')
        return response.result
      })
      .then((botId) => api.getBot(botId))
      .then((resp) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities).toEqual('object')
        return response.result
      })
      .then((botId) =>
        api.updateBot(botId, {
            bot: {
              name: 'abc',
              description: 'cde',
            },
          })
          .then((resp) => {
            expect(typeof resp.response.result).toEqual('number')
            expect(typeof resp.response.entities).toEqual('object')
          })
          .then(() => api.updateBotDefRevisions(botId,
            mockUpdatedBot,
          ))
          .then((resp) => {
            const botId = resp.response.result
            const entities = resp.response.entities
            expect(typeof botId).toEqual('number')
            expect(typeof entities.bots[botId]).toEqual('object')
          })
          .then(() => api.deployBot(botId))
          .then((resp) => {
            const botId = resp.response.result
            const entities = resp.response.entities
            expect(typeof botId).toEqual('number')
            expect(typeof entities.bots[botId]).toEqual('object')
            expect(typeof entities.bots[botId].version).toEqual('number')
          })
          .then(() => api.listBotDefRevisions(botId))
          .then((resp) => {
            const botId = resp.response.result
            const entities = resp.response.entities
            expect(typeof botId).toEqual('number')
            expect(typeof entities.bots[botId]).toEqual('object')
            expect(Array.isArray(entities.bots[botId].botDefs)).toEqual(true)
            expect(entities.bots[botId].botDefs.length).toBeGreaterThan(0)
            expect(entities.bots[botId].botDefs[0].botId).toEqual(botId)
            return entities.bots[botId].botDefs[0].version
          })
          .then(version => api.getBotDefRevision(botId, version))
          .then((resp) => {
            const botId = resp.response.result
            const entities = resp.response.entities
            expect(typeof botId).toEqual('number')
            expect(typeof entities.bots[botId]).toEqual('object')
            expect(typeof entities.bots[botId].botJson.bot).toEqual('object')
          })
      )
      .catch((error) => console.log(error))
  )

  it('should test the platform APIs', () =>
    delay(DELAY_MSECONDS)
      .then(() => api.signup('tester3@gmail.com', '123123', 'Asia/Taipei'))
      .then(() => api.login('tester3@gmail.com', '123123'))
      .then((resp) => { storage.set(AUTH_TOKEN, resp.response.authToken) })
      .then(() => api.createPlatform(mockPlatform))
      .then((resp) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities).toEqual('object')
        return response.result
      })
      .then((platformId) => api.getPlatform(platformId))
      .then((resp) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities).toEqual('object')
        return response.result
      })
      .then((platformId) =>
        api.updatePlatform(platformId, Object.assign(mockPlatform, {
            name: 'platform 2'
          }))
          .then(resp => ({
            platformId, resp,
          }))
      )
      .then(({ platformId, resp }) => {
        const response = resp.response
        expect(response.entities.platforms[platformId].name).toEqual('platform 2')
        expect(response.result).toEqual(platformId)
        return platformId
      })
      .then(() => api.getPlatforms())
      .then((resp) => {
        const platformsIds = resp.response.result
        const platforms = resp.response.entities.platforms
        expect(Array.isArray(platformsIds)).toEqual(true)
        expect(platformsIds.length).toBeGreaterThan(0)
        expect(Object.keys(platforms).length).toEqual(platformsIds.length)
        return platformsIds[platformsIds.length - 1]
      })
      .then(platformId => api.deletePlatform(platformId))
      .then((resp) => {
        expect(resp.response.message).toEqual('ok')
      })
      .catch((error) => console.log(error))
  )

  it('should test the broadcast APIs', () =>
    delay(DELAY_MSECONDS)
      .then(() => api.signup('tester4@gmail.com', '123123', 'Asia/Taipei'))
      .then(() => api.login('tester4@gmail.com', '123123'))
      .then((resp) => { storage.set(AUTH_TOKEN, resp.response.authToken) })
      .then(() => api.createBot(mockBot))
      .then((resp) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities).toEqual('object')
        return response.result
      })
      .then((botId) =>
        api.createBroadcast(Object.assign(mockBroadcast, { botId }))
          .then(resp => ({ botId, resp }))
      )
      .then(({ botId, resp }) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities.broadcasts).toEqual('object')
        expect(response.entities.broadcasts[response.result].name).toEqual(mockBroadcast.name)
        return botId
      })
      .then((botId) => api.getAllBroadcasts(botId))
      .then((resp) => {
        const broadcastIds = resp.response.result
        const broadcasts = resp.response.entities.broadcasts
        expect(Array.isArray(broadcastIds)).toEqual(true)
        expect(broadcastIds.length).toBeGreaterThan(0)
        expect(Object.keys(broadcasts).length).toEqual(broadcastIds.length)
        return broadcastIds[broadcastIds.length - 1]
      })
      .then((broadcastId) => api.getBroadcast(broadcastId))
      .then((resp) => {
        const response = resp.response
        expect(typeof response.result).toEqual('number')
        expect(typeof response.entities.broadcasts).toEqual('object')
        expect(response.entities.broadcasts[response.result].name).toEqual(mockBroadcast.name)
        return response.result
      })
      .then((broadcastId) =>
        api.updateBroadcast(broadcastId, Object.assign(mockBroadcast, {
            name: 'broadcast1-1'
          }))
          .then(resp => ({
            broadcastId, resp,
          }))
      )
      .then(({ broadcastId, resp }) => {
        expect(resp.response.result).toEqual(broadcastId)
        expect(typeof resp.response.entities.broadcasts).toEqual('object')
        return broadcastId
      })
      .then(broadcastId => api.deleteBroadcast(broadcastId))
      .then((resp) => {
        expect(resp.response.message).toEqual('ok')
      })
      .catch((error) => console.log(error))
  )
})
