from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^publish/(\d+)/$', views.publish, name="youtube_publish"),
    url(r'^convert/(\d+)/$', views.publish, {'publish': False}, name="youtube_convert"),
]
