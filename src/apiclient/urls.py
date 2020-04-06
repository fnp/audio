from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^oauth/$', views.oauth, name='apiclient_oauth'),
    url(r'^oauth_callback/$', views.oauth_callback, name='apiclient_oauth_callback'),
    url(r'^oauth2/$', views.oauth2, name='apiclient_oauth2'),
    url(r'^oauth2_redirect/$', views.oauth2_redirect, name='apiclient_oauth2_redirect'),
]
