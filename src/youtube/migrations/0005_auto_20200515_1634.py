# Generated by Django 3.0.4 on 2020-05-15 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0004_auto_20200504_1148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='youtube',
            old_name='card',
            new_name='loop_card',
        ),
        migrations.AddField(
            model_name='youtube',
            name='thumbnail_definition',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.SmallIntegerField()),
                ('image', models.FileField(upload_to='youtube/card')),
                ('duration', models.FloatField()),
                ('youtube', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube.YouTube')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
    ]
