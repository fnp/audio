# Generated by Django 3.0.4 on 2020-03-30 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='youtube',
            name='category',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='youtube',
            name='intro_card_length',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='youtube',
            name='outro_card_length',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
