import requests

from bb8 import config


def verify_facebook(access_token):
    facebook_app_id = config.FACEBOOK_APP_ID
    facebook_app_secret = config.FACEBOOK_APP_SECRET
    facebook_app_access_token = '%s|%s' % (
        facebook_app_id, facebook_app_secret)

    res = requests.get(
        'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s'
        % (access_token, facebook_app_access_token)).json()

    if not res['data']['is_valid']:
        raise RuntimeError('The access token is invalid')
    return res['data']['user_id']
