# Generated by Django 3.0.4 on 2020-05-24 01:40

import json
from django.db import migrations


def populate_license(apps, schema_editor):
    License = apps.get_model('archive.License')
    Audiobook = apps.get_model('archive.Audiobook')
    licenses = {}
    for a in Audiobook.objects.all():
        if a.mp3_tags:
            tags = json.loads(a.mp3_published_tags)
            uri = tags.get('license')
            if not uri:
                continue
            if uri not in licenses:
                licenses[uri], created = License.objects.get_or_create(uri=uri, defaults={"name": "?"})
            a.license = licenses[uri]
            a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0009_auto_20200524_0139'),
    ]

    operations = [
        migrations.RunPython(
            populate_license,
            migrations.RunPython.noop
        )
    ]
