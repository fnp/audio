from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': 'new/'}),

    url(r'^new/$', 'archive.views.list_new', name="list_new"),
    url(r'^new/(.+)/$', 'archive.views.file_new', name="file_new"),
    url(r'^move_to_archive/(.+)/$', 'archive.views.move_to_archive', name="move_to_archive"),

    url(r'^unpublished/$', 'archive.views.list_unpublished', name="list_unpublished"),
    url(r'^publishing/$', 'archive.views.list_publishing', name="list_publishing"),
    url(r'^published/$', 'archive.views.list_published', name="list_published"),
    url(r'^file/(\d+)/$', 'archive.views.file_managed', name="file"),
    url(r'^publish/(\d+)/$', 'archive.views.publish', name="publish"),
    url(r'^convert/(\d+)/$', 'archive.views.publish', {'publish': False}, name="convert"),
    url(r'^cancel/(\d+)/$', 'archive.views.cancel_publishing', name="cancel_publishing"),
    url(r'^remove_to_archive/(\d+)/$', 'archive.views.remove_to_archive', name="remove_to_archive"),

    url(r'^unmanaged/$', 'archive.views.list_unmanaged', name="list_unmanaged"),
    url(r'^unmanaged/(.+)/$', 'archive.views.file_unmanaged', name="file_unmanaged"),
    url(r'^move_to_new/(.+)/$', 'archive.views.move_to_new', name="move_to_new"),
)
