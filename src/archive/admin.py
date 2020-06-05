from archive.models import Project, Audiobook, Piece, License
from django.contrib import admin

admin.site.register(Project)


class AudiobookAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "index", "part_name", "license", "youtube_volume"]
    list_filter = ["license"]
    search_fields = ["title", "slug", "part_name", "youtube_volume"]
    list_editable = ["youtube_volume"]


admin.site.register(Audiobook, AudiobookAdmin)
admin.site.register(Piece)
admin.site.register(License)
