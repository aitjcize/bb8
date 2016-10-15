import fetch from './util';

const auth = {
  login(email, passwd) {
    fetch('POST', '/login', {
      email, passwd,
    })
    .then(response => ({ response: response.json() }))
    .catch(error => ({ error }));
  },
};

export default auth;
