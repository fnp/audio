import requests
from requests_oauthlib import OAuth1
from apiclient.settings import WL_CONSUMER_KEY, WL_CONSUMER_SECRET, WL_API_URL


class ApiError(BaseException):
    pass


class NotAuthorizedError(BaseException):
    pass


def api_call(user, path, method='POST', data=None, files=None):
    from .models import OAuthConnection
    conn = OAuthConnection.get(user=user)
    if not conn.access:
        raise NotAuthorizedError("No WL authorization for user %s." % user)

    auth = OAuth1(WL_CONSUMER_KEY, WL_CONSUMER_SECRET, conn.token, conn.token_secret)

    url = WL_API_URL + path

    r = requests.request(method=method, url=url, data=data, files=files, auth=auth)

    if r.status_code == 200:
        return r.content
    elif 201 <= r.status_code < 300:
        return
    elif r.status_code == 401:
        raise ApiError('User not authorized for publishing.')
    else:
        raise ApiError("WL API call error %s, path: %s" % (r.status_code, path))

