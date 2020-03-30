from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
import requests
from requests_oauthlib import OAuth1Session

from apiclient.models import OAuthConnection
from apiclient.settings import WL_CONSUMER_KEY, WL_CONSUMER_SECRET
from apiclient.settings import WL_REQUEST_TOKEN_URL, WL_ACCESS_TOKEN_URL, WL_AUTHORIZE_URL


@login_required
def oauth(request):
    oauth = OAuth1Session(WL_CONSUMER_KEY, WL_CONSUMER_SECRET)
    request_token = oauth.fetch_request_token(WL_REQUEST_TOKEN_URL)

    conn = OAuthConnection.get(request.user)
    conn.access = False
    conn.token = request_token['oauth_token']
    conn.token_secret = request_token['oauth_token_secret']
    conn.save()

    url = oauth.authorization_url(WL_AUTHORIZE_URL)
    url += '&oauth_callback=' + request.build_absolute_uri(reverse("apiclient_oauth_callback"))
    return HttpResponseRedirect(url)


@login_required
def oauth_callback(request):
    conn = OAuthConnection.get(request.user)
    oauth_verifier = request.GET.get('oauth_verifier', 'verifier')

    oauth = OAuth1Session(
        WL_CONSUMER_KEY, WL_CONSUMER_SECRET,
                          conn.token, conn.token_secret,
                          verifier=oauth_verifier)
    access_token = oauth.fetch_access_token(WL_ACCESS_TOKEN_URL)

    conn.access = True
    conn.token = access_token['oauth_token']
    conn.token_secret = access_token['oauth_token_secret']
    conn.save()

    return HttpResponseRedirect('/')
