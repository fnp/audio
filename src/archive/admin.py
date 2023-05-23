from archive.models import Project, Audiobook, License, Config
from django.contrib import admin

admin.site.register(Project)


class AudiobookAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "index", "part_name", "duration", "license", "youtube_volume"]
    list_filter = [
        "license",
        "project",
        ("mp3_published", admin.EmptyFieldListFilter),
        ("youtube_published", admin.EmptyFieldListFilter),
    ]
    search_fields = ["title", "slug", "part_name", "youtube_volume"]
    list_editable = ["youtube_volume"]
    readonly_fields = ['duration']


admin.site.register(Audiobook, AudiobookAdmin)
admin.site.register(License)
admin.site.register(Config)
