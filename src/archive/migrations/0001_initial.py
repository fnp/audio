from django.db import models, migrations
import archive.utils
import archive.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Audiobook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_file', models.FileField(verbose_name='source file', max_length=255, editable=False, upload_to=archive.models.source_upload_to)),
                ('source_sha1', models.CharField(max_length=40, editable=False)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('part_name', models.CharField(default='', help_text='eg. chapter in a novel', max_length=255, verbose_name='part name', blank=True)),
                ('index', models.IntegerField(default=0, verbose_name='index')),
                ('parts_count', models.IntegerField(default=1, verbose_name='parts count')),
                ('artist', models.CharField(max_length=255, verbose_name='artist')),
                ('conductor', models.CharField(max_length=255, verbose_name='conductor')),
                ('encoded_by', models.CharField(max_length=255, verbose_name='encoded by')),
                ('date', models.CharField(max_length=255, verbose_name='date')),
                ('url', models.URLField(max_length=255, verbose_name='book url')),
                ('translator', models.CharField(max_length=255, null=True, verbose_name='translator', blank=True)),
                ('modified', models.DateTimeField(null=True, editable=False)),
                ('mp3_status', models.SmallIntegerField(null=True, editable=False, choices=[(1, 'Waiting'), (2, 'Encoding'), (3, 'Tagging'), (4, 'Sending')])),
                ('mp3_task', models.CharField(max_length=64, null=True, editable=False)),
                ('mp3_tags', models.TextField(null=True, editable=False)),
                ('mp3_file', models.FileField(storage=archive.utils.OverwriteStorage(), upload_to='archive/final', null=True, editable=False)),
                ('mp3_published_tags', models.TextField(null=True, editable=False)),
                ('mp3_published', models.DateTimeField(null=True, editable=False)),
                ('ogg_status', models.SmallIntegerField(null=True, editable=False, choices=[(1, 'Waiting'), (2, 'Encoding'), (3, 'Tagging'), (4, 'Sending')])),
                ('ogg_task', models.CharField(max_length=64, null=True, editable=False)),
                ('ogg_tags', models.TextField(null=True, editable=False)),
                ('ogg_file', models.FileField(storage=archive.utils.OverwriteStorage(), upload_to='archive/final', null=True, editable=False)),
                ('ogg_published_tags', models.TextField(null=True, editable=False)),
                ('ogg_published', models.DateTimeField(null=True, editable=False)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'audiobook',
                'verbose_name_plural': 'audiobooks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, verbose_name='Nazwa', db_index=True)),
                ('sponsors', models.TextField(null=True, verbose_name='Sponsorzy', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='audiobook',
            name='project',
            field=models.ForeignKey(verbose_name='project', to='archive.Project', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
