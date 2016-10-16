import fetch from './util';

const auth = {
  login(email, passwd) {
    return fetch('POST', '/api/login', {
      email, passwd,
    })
    .then(response => ({ response }))
    .catch(error => ({ error }));
  },
};

export default auth;
