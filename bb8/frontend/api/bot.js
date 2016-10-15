import fetch from './util';

const bot = {
  fetchAll() {
    fetch('GET', '/bots', {})
      .then(response => ({ response: response.json().bots }))
      .catch(error => ({ error }));
  },
};

export default bot;
