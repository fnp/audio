# Generated by Django 3.1.2 on 2020-10-22 14:15

from django.db import migrations


def populate_youtube_relations(apps, schema_editor):
    YouTube = apps.get_model('youtube', 'YouTube')
    ThumbnailTemplate = apps.get_model('youtube', 'ThumbnailTemplate')
    Project = apps.get_model('archive', 'Project')

    try:
        yt = YouTube.objects.first()
    except YouTube.DoesNotExist:
        yt = YouTube.objects.create(name='default')

    Project.objects.filter(youtube=None).update(youtube=yt)
    ThumbnailTemplate.objects.filter(youtube=None).update(youtube=yt)


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0015_auto_20201022_1414'),
        ('archive', '0019_auto_20201022_1414'),
    ]

    operations = [
        migrations.RunPython(
            populate_youtube_relations,
            migrations.RunPython.noop
        )
    ]
