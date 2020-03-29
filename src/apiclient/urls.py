# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^oauth/$', views.oauth, name='apiclient_oauth'),
    url(r'^oauth_callback/$', views.oauth_callback, name='apiclient_oauth_callback'),
]