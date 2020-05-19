# Generated by Django 3.0.4 on 2020-05-18 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0007_auto_20200515_1645'),
    ]

    operations = [
        migrations.CreateModel(
            name='Font',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('truetype', models.FileField(upload_to='youtube/font')),
            ],
        ),
    ]