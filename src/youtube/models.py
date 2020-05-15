import io
from os import unlink
from tempfile import NamedTemporaryFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template import Template, Context
from apiclient import youtube_call
from .utils import (
    video_from_image,
    cut_video,
    concat_videos,
    get_duration,
    get_framerate,
    mux,
)
from .thumbnail import create_thumbnail


class YouTube(models.Model):
    title_template = models.CharField(max_length=1024, blank=True)
    description_template = models.TextField(blank=True)
    category = models.IntegerField(null=True, blank=True)  # get categories
    loop_card = models.FileField(upload_to='youtube/card', blank=True)
    loop_video = models.FileField(upload_to='youtube/loop_video', blank=True)
    thumbnail_template = models.FileField(upload_to='youtube/thumbnail', blank=True)
    thumbnail_definition = models.TextField(blank=True)
    genres = models.CharField(max_length=2048, blank=True)

    class Meta:
        verbose_name = _("YouTube configuration")
        verbose_name_plural = _("YouTube configurations")

    def publish(self, audiobook, path):
        ctx = Context(dict(audiobook=audiobook))
        description = Template(self.description_template).render(ctx)
        title = Template(self.title_template).render(ctx)
        privacy = 'private'

        data = dict(
            snippet=dict(
                title=title,
                description=description,
                # tags=tags,
                # categoryId=category,
                # defaultLanguage
            ),
            status=dict(
                privacyStatus=privacy,
                # license
                # selfDeclaredMadeForKids
            ),
            # recordingDetails=dict(
            # recordingDate
            # ),
        )
        part = ",".join(data.keys())

        with open(path, "rb") as f:
            response = youtube_call(
                "POST",
                "https://www.googleapis.com/upload/youtube/v3/videos",
                params={'part': part},
                data=data,
                media_data=f.read(),
            )
        data = response.json()
        audiobook.youtube_id = data['id']
        audiobook.save(update_fields=['youtube_id'])

        self.update_thumbnail(audiobook)
        return response

    def prepare_file(self, input_path, output_path=None):
        duration = get_duration(input_path)
        video = self.prepare_video(duration)
        output = mux([video, input_path], output_path=output_path)
        unlink(video)
        return output

    def prepare_video(self, duration):
        concat = []
        outro = []
        delete = []

        if self.loop_video:
            fps = get_framerate(self.loop_video.path)
        else:
            fps = 25

        loop_duration = duration
        for card in self.card_set.filter(order__lt=0, duration__gt=0):
            loop_duration -= card.duration
            card_video = video_from_image(
                card.image.path, card.duration, fps=fps
            )
            (concat if card.order < 0 else outro).append(card_video)
            delete.append(intro)

        if self.loop_video:
            loop_video_duration = get_duration(self.loop_video.path)
            times_loop = int(loop_duration // loop_video_duration)

            leftover_duration = loop_duration % loop_video_duration
            leftover = cut_video(self.loop_video.path, leftover_duration)
            concat.extend([self.loop_video.path] * times_loop + [leftover])
            delete.append(leftover)
        else:
            leftover = video_from_image(self.loop_card.path, loop_duration)
            concat.append(video_from_image(self.loop_card.path, loop_duration, fps=fps))
            delete.append(leftover)
        concat.extend(outro)

        output = concat_videos(concat)
        for p in delete:
            unlink(p)
        return output

    # tags
    # license
    # selfDeclaredMadeForKids

    def update_thumbnail(self, audiobook):
        thumbnail = self.prepare_thumbnail(audiobook)
        response = youtube_call(
            "POST",
            "https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
            params={'videoId': audiobook.youtube_id},
            media_data=buf.read(),  # Or just data?
        )

    def prepare_thumbnail(self, audiobook):
        img = create_thumbnail(
            self.thumbnail_template.path,
            self.thumbnail_definition,
            {}, # TODO proper context
            lambda name: Font.objects.get(name=name).truetype.path
        )
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf
        

class Card(models.Model):
    youtube = models.ForeignKey(YouTube, models.CASCADE)
    order = models.SmallIntegerField()
    image = models.FileField(upload_to='youtube/card')
    duration = models.FloatField()

    class Meta:
        ordering = ('order', )


class Font(models.Model):
    name = models.CharField(max_length=255, unique=True)
    truetype = models.FileField(upload_to='youtube/font')

    def __str__(self):
        return self.name
