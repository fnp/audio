# Generated by Django 3.0.6 on 2020-07-06 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0012_move_thumbnail_definitions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='youtube',
            name='thumbnail_definition',
        ),
        migrations.RemoveField(
            model_name='youtube',
            name='thumbnail_template',
        ),
    ]
