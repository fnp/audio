# Generated by Django 3.1.2 on 2021-01-21 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0018_auto_20200703_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiobook',
            name='duration',
            field=models.FloatField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='audiobook',
            name='mp3_status',
            field=models.SmallIntegerField(choices=[(5, 'Queued'), (10, 'Waiting'), (20, 'Encoding'), (30, 'Tagging'), (40, 'Converting audio'), (50, 'Converting video'), (60, 'Assembling audio'), (70, 'Assembling video'), (80, 'Joining audio and video'), (100, 'Sending'), (110, 'Setting thumbnail')], editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='audiobook',
            name='ogg_status',
            field=models.SmallIntegerField(choices=[(5, 'Queued'), (10, 'Waiting'), (20, 'Encoding'), (30, 'Tagging'), (40, 'Converting audio'), (50, 'Converting video'), (60, 'Assembling audio'), (70, 'Assembling video'), (80, 'Joining audio and video'), (100, 'Sending'), (110, 'Setting thumbnail')], editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='audiobook',
            name='youtube_status',
            field=models.SmallIntegerField(choices=[(5, 'Queued'), (10, 'Waiting'), (20, 'Encoding'), (30, 'Tagging'), (40, 'Converting audio'), (50, 'Converting video'), (60, 'Assembling audio'), (70, 'Assembling video'), (80, 'Joining audio and video'), (100, 'Sending'), (110, 'Setting thumbnail')], editable=False, null=True),
        ),
    ]
