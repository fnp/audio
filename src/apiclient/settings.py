from django.conf import settings


WL_CONSUMER_KEY = getattr(settings, 'APICLIENT_WL_CONSUMER_KEY', None)
WL_CONSUMER_SECRET = getattr(settings, 'APICLIENT_WL_CONSUMER_SECRET', None)

WL_API_URL = getattr(settings, 'APICLIENT_WL_API_URL', 'https://wolnelektury.pl/api/')

WL_REQUEST_TOKEN_URL = getattr(settings, 'APICLIENT_WL_REQUEST_TOKEN_URL',
        WL_API_URL + 'oauth/request_token/')
WL_ACCESS_TOKEN_URL = getattr(settings, 'APICLIENT_WL_ACCESS_TOKEN_URL',
        WL_API_URL + 'oauth/access_token/')
WL_AUTHORIZE_URL = getattr(settings, 'APICLIENT_WL_AUTHORIZE_URL',
        WL_API_URL + 'oauth/authorize/')


YOUTUBE_SCOPE = [
    'https://www.googleapis.com/auth/youtube',
]
YOUTUBE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
YOUTUBE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
YOUTUBE_CLIENT_ID = getattr(settings, 'YOUTUBE_CLIENT_ID', None)
YOUTUBE_CLIENT_SECRET = getattr(settings, 'YOUTUBE_CLIENT_SECRET', None)

