from django.contrib import admin
from . import models


class CardInline(admin.TabularInline):
    model = models.Card


class YouTubeAdmin(admin.ModelAdmin):
    inlines = [CardInline]


admin.site.register(models.YouTube, YouTubeAdmin)


admin.site.register(models.Font)


class ThumbnailTemplateAdmin(admin.ModelAdmin):
    list_display = ['order', 'collections', 'authors', 'epochs', 'genres', 'kinds']

admin.site.register(models.ThumbnailTemplate, ThumbnailTemplateAdmin)
