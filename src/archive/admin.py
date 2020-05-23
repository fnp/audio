from archive.models import Project, Audiobook, Piece, License
from django.contrib import admin

admin.site.register(Project)


class AudiobookAdmin(admin.ModelAdmin):
    list_filter = ['license']


admin.site.register(Audiobook, AudiobookAdmin)
admin.site.register(Piece)
admin.site.register(License)
