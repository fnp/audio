from django.conf.urls import url
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='new/')),

    url(r'^new/$', views.list_new, name="list_new"),
    url(r'^new/(.+)/$', views.file_new, name="file_new"),
    url(r'^move_to_archive/(.+)/$', views.move_to_archive, name="move_to_archive"),

    url(r'^unpublished/$', views.list_unpublished, name="list_unpublished"),
    url(r'^publishing/$', views.list_publishing, name="list_publishing"),
    url(r'^published/$', views.list_published, name="list_published"),
    url(r'^file/(\d+)/$', views.file_managed, name="file"),
    url(r'^publish/(\d+)/$', views.publish, name="publish"),
    url(r'^convert/(\d+)/$', views.publish, {'publish': False}, name="convert"),
    url(r'^download/(\d+)/$', views.download, name="download"),
    url(r'^download/(\d+)\.(mp3|ogg)$', views.download, name="download"),
    url(r'^cancel/(\d+)/$', views.cancel_publishing, name="cancel_publishing"),
    url(r'^remove_to_archive/(\d+)/$', views.remove_to_archive, name="remove_to_archive"),

    url(r'^unmanaged/$', views.list_unmanaged, name="list_unmanaged"),
    url(r'^unmanaged/(.+)/$', views.file_unmanaged, name="file_unmanaged"),
    url(r'^move_to_new/(.+)/$', views.move_to_new, name="move_to_new"),
]
