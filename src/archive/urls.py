from django.conf.urls import url
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", views.AudiobookList.as_view(), name="list_managed"),
    url(r'^new/$', views.list_new, name="list_new"),
    url(r'^new/(.+)/$', views.file_new, name="file_new"),
    url(r'^move_to_archive/(.+)/$', views.move_to_archive, name="move_to_archive"),
    url(r'^publishing/$', views.list_publishing, name="list_publishing"),
    path('book/<slug:slug>/', views.BookView.as_view(), name="book"),
    url(r'^file/(\d+)/$', views.file_managed, name="file"),
    url(r'^publish/(\d+)/$', views.publish, name="publish"),
    url(r'^convert/(\d+)/$', views.publish, {'publish': False}, name="convert"),
    url(r'^download/(\d+)/$', views.download, name="download"),
    url(r'^download/(\d+)\.(mp3|ogg|mkv)$', views.download, name="download"),
    url(r'^cancel/(\d+)/$', views.cancel_publishing, name="cancel_publishing"),
    url(r'^remove_to_archive/(\d+)/$', views.remove_to_archive, name="remove_to_archive"),
    url(r'^unmanaged/$', views.list_unmanaged, name="list_unmanaged"),
    url(r'^unmanaged/(.+)/$', views.file_unmanaged, name="file_unmanaged"),
    url(r'^move_to_new/(.+)/$', views.move_to_new, name="move_to_new"),
]
