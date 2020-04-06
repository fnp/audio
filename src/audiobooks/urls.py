from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import RedirectView
import django_cas_ng.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='archive/', permanent=False)),
    url(r'^archive/', include('archive.urls')),
    url(r'^youtube/', include('youtube.urls')),
    url(r'^publish/', include('apiclient.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', django_cas_ng.views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', django_cas_ng.views.LogoutView.as_view(), name='logout'),
]
