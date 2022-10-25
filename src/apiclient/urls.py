from django.urls import path
from . import views


urlpatterns = [
    path('oauth/', views.oauth, name='apiclient_oauth'),
    path('auth_callback/', views.oauth_callback, name='apiclient_oauth_callback'),
    path('oauth2/', views.oauth2, name='apiclient_oauth2'),
    path('oauth2_redirect/', views.oauth2_redirect, name='apiclient_oauth2_redirect'),
]
