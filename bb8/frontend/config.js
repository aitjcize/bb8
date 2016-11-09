const HTTP_PORT = process.env.HTTP_PORT

const constants = {
  dev: {
    LINE_WEBHOOK: `https://dev.compose.ai:${HTTP_PORT}/bot/line/`,
  },
  prod: {
    LINE_WEBHOOK: `https://dev.compose.ai:${HTTP_PORT}/bot/line/`,
  },
}

if (process.env.BB8_DEPLOY) {
  module.exports = constants.prod
} else {
  module.exports = constants.dev
}
