const constants = {
  dev: {
  },
  prod: {
  },
};

if (process.env.BB8_DEPLOY) {
  module.exports = constants.prod;
} else {
  module.exports = constants.dev;
}
