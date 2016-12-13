import requests

FACEBOOK_APP_ID = '1797497130479857'
FACEBOOK_APP_SECRET = '132f7214f7753be8ff8d235af0b7bd20'

FACEBOOK_APP_ACCESS_TOKEN = '%s|%s' % (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)


def verify_facebook(access_token):
    res = requests.get(
        'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s'
        % (access_token, FACEBOOK_APP_ACCESS_TOKEN)).json()

    if not res['data']['is_valid']:
        raise RuntimeError('The access token is invalid')
    return res['data']['user_id']
