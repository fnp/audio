# Generated by Django 3.0.4 on 2020-05-15 16:34

from django.db import migrations


def move_cards(apps, schema_editor):
    YouTube = apps.get_model('youtube', 'YouTube')
    Card = apps.get_model('youtube', 'Card')
    for yt in YouTube.objects.all():
        if yt.intro_card:
            Card.objects.create(
                youtube=yt,
                image=yt.intro_card,
                duration=yt.intro_card_duration or 0,
                order=-1
            )
        if yt.outro_card:            
            Card.objects.create(
                youtube=yt,
                image=yt.outro_card,
                duration=yt.outro_card_duration or 0,
                order=1
            )
        yt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0005_auto_20200515_1634'),
    ]

    operations = [
        migrations.RunPython(
            move_cards,
            migrations.RunPython.noop,
        )
    ]
