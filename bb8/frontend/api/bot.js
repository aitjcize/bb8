import fetch from './util'

const bot = {
  getAllBots() {
    return fetch('GET', '/api/bots', {})
      .then(response => ({ response: response.bots }))
      .catch(error => ({ error }))
  },
}

export default bot
