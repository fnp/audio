from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib import admin
import django_cas_ng.views


urlpatterns = [
    path('', RedirectView.as_view(url='archive/', permanent=False)),
    path('archive/', include('archive.urls')),
    path('youtube/', include('youtube.urls')),
    path('publish/', include('apiclient.urls')),

    path('admin/', admin.site.urls),
    path('accounts/login/', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
    path('accounts/logout/', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
]
