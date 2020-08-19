from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^publish/(\d+)/$', views.publish, name="youtube_publish"),
    path('book/<slug:slug>/publish/', views.book_publish, name="youtube_book_publish"),
    path('thumbnail/<int:aid>/', views.thumbnail, name='youtube_thumbnail'),
    path('thumbnail/<int:aid>/<int:thumbnail_id>/', views.thumbnail, name='youtube_thumbnail'),
    path('preview/<int:pk>/', views.Preview.as_view(), name="youtube_preview"),
    path('update/<int:pk>/', views.Update.as_view(), name="youtube_update"),
    path('update-thumbnail/<int:pk>/', views.UpdateThumbnail.as_view(), name="youtube_update_thumbnail"),
]
