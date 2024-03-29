# Generated by Django 3.1.14 on 2021-12-22 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0023_project_info_flac'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('intro_flac', models.FileField(blank=True, upload_to='config/intro_flac')),
                ('intro_min_seconds', models.IntegerField()),
                ('outro_flac', models.FileField(blank=True, upload_to='config/outro_flac')),
                ('outro_min_seconds', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Configuration',
                'verbose_name_plural': 'Configurations',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='config',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='archive.config'),
        ),
    ]
