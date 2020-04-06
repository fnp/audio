import json
from django.db import models
from django.contrib.auth.models import User
from requests_oauthlib import OAuth2Session
from .settings import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_TOKEN_URL


class OAuthConnection(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    access = models.BooleanField(default=False)
    token = models.CharField(max_length=64, null=True, blank=True)
    token_secret = models.CharField(max_length=64, null=True, blank=True)

    @classmethod
    def get(cls, user):
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            o = cls(user=user)
            o.save()
            return o


class YouTubeToken(models.Model):
    token = models.TextField()

    def token_updater(self, token):
        self.token = json.dumps(token)
        self.save()

    def get_session(self):
        return OAuth2Session(
            client_id=YOUTUBE_CLIENT_ID,
            auto_refresh_url=YOUTUBE_TOKEN_URL,
            token=json.loads(self.token),
            auto_refresh_kwargs={'client_id':YOUTUBE_CLIENT_ID,'client_secret':YOUTUBE_CLIENT_SECRET},
            token_updater=self.token_updater
        )

    def call(self, method, url, params=None, data=None, media_data=None):
        params = params or {}
        params['uploadType'] = 'resumable'

        session = self.get_session()
        response = session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers={
                'X-Upload-Content-Length': str(len(media_data)),
                'x-upload-content-type': 'application/octet-stream',
            }
        )
        location = response.headers['Location']
        return session.put(
            url=location,
            data=media_data,
            headers={"Content-Type": "application/octet-stream"},
        )
