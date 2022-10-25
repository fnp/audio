from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", views.AudiobookList.as_view(), name="list_managed"),
    path('new/', views.list_new, name="list_new"),
    path('new/<path:filename>/', views.file_new, name="file_new"),
    path('move_to_archive/<path:filename>/', views.move_to_archive, name="move_to_archive"),
    path('publishing/', views.list_publishing, name="list_publishing"),
    path('book/<slug:slug>/', views.BookView.as_view(), name="book"),
    path('book-youtube-volume/<int:aid>/', views.book_youtube_volume, name="book_youtube_volume"),
    path('file/<int:id>/', views.file_managed, name="file"),
    path('publish/<int:aid>/', views.publish, name="publish"),
    path('convert/<int:aid>/', views.publish, {'publish': False}, name="convert"),
    path('download/<int:aid>/', views.download, name="download"),
    path('download/<int:aid>.<slug:which>', views.download, name="download"),
    path('cancel/<int:aid>/', views.cancel_publishing, name="cancel_publishing"),
    path('remove_to_archive/<int:aid>/', views.remove_to_archive, name="remove_to_archive"),
    path('unmanaged/', views.list_unmanaged, name="list_unmanaged"),
    path('unmanaged/<path:filename>/', views.file_unmanaged, name="file_unmanaged"),
    path('move_to_new/<path:filename>/', views.move_to_new, name="move_to_new"),
]
