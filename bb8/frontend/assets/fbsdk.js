/* eslint-disable */
window.fbAsyncInit = () => {
  FB.init({
    appId: process.env.BB8_DEPLOY ? '1797497130479857' : '1663575030609051',
    cookie: true,
    xfbml: true,
    version: 'v2.8',
  })
}

(function(d, s, id){
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {return;}
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
