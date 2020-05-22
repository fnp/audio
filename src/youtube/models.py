import io
from os import unlink
from tempfile import NamedTemporaryFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template import Template, Context
from apiclient import youtube_call
from archive.settings import LICENSE, LICENSE_NAME
from .utils import (
    concat_audio,
    concat_videos,
    cut_video,
    get_duration,
    get_framerate,
    mux,
    standardize_audio,
    standardize_video,
    video_from_image,
)
from .thumbnail import create_thumbnail


class YouTube(models.Model):
    title_template = models.CharField(max_length=1024, blank=True)
    description_template = models.TextField(blank=True)
    category = models.IntegerField(null=True, blank=True, choices=[
        (27, 'Edukacja'),
    ])
    intro_flac = models.FileField(upload_to='youtube/intro_flac', blank=True)
    outro_flac = models.FileField(upload_to='youtube/outro_flac', blank=True)
    loop_card = models.FileField(upload_to='youtube/card', blank=True)
    loop_video = models.FileField(upload_to='youtube/loop_video', blank=True)
    thumbnail_template = models.FileField(upload_to='youtube/thumbnail', blank=True)
    thumbnail_definition = models.TextField(blank=True)
    privacy_status = models.CharField(max_length=16, choices=[
        ('public', _('public')),
        ('unlisted', _('unlisted')),
        ('private', _('private')),
    ])
    genres = models.CharField(max_length=2048, blank=True)

    class Meta:
        verbose_name = _("YouTube configuration")
        verbose_name_plural = _("YouTube configurations")

    def get_context(self, audiobook):
        return Context(dict(
            audiobook=audiobook,
            LICENSE=LICENSE,
            LICENSE_NAME=LICENSE_NAME,
        ))

    def get_description(self, audiobook):
        return Template(self.description_template).render(self.get_context(audiobook))

    def get_title(self, audiobook):
        return Template(self.title_template).render(self.get_context(audiobook))

    def get_data(self, audiobook):
        return dict(
            snippet=dict(
                title=self.get_title(audiobook),
                description=self.get_description(audiobook),
                categoryId=self.category,
                defaultLanguage='pl',
                defaultAudioLanguage='pl',
            ),
            status=dict(
                privacyStatus=self.privacy_status,
            ),
        )

    def publish(self, audiobook, path):
        data = self.get_data(audiobook)
        part = ",".join(data.keys())

        response = youtube_call(
            "POST",
            "https://www.googleapis.com/upload/youtube/v3/videos",
            params={'part': part},
            json=data,
            resumable_file_path=path,
        )
        data = response.json()
        audiobook.youtube_id = data['id']
        audiobook.save(update_fields=['youtube_id'])

        self.update_thumbnail(audiobook)
        return response

    def update_data(self, audiobook):
        data = self.get_data(audiobook)
        data['id'] = audiobook.youtube_id
        part = ",".join(data.keys())
        youtube_call(
            "PUT",
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": part},
            json=data
        )       

    def prepare_file(self, input_path, output_path=None):
        audio = self.prepare_audio(input_path)
        duration = self.get_duration(input_path)
        video = self.prepare_video(duration)
        output = mux([video, audio], output_path=output_path)
        unlink(audio)
        unlink(video)
        return output

    def get_duration(self, input_path):
        d = get_duration(input_path)
        if self.intro_flac:
            d += get_duration(self.intro_flac.path)
        if self.outro_flac:
            d += get_duration(self.outro_flac.path)
        return d
    
    def prepare_audio(self, input_path):
        files = []
        if self.intro_flac:
            files.append(standardize_audio(self.intro_flac.path))
        files.append(standardize_audio(input_path, cache=False))
        if self.outro_flac:
            files.append(standardize_audio(self.outro_flac.path))
        output = concat_audio(files)
        for d in files:
            unlink(d)
        return output

    
    def prepare_video(self, duration):
        concat = []
        outro = []
        delete = []

        if self.loop_video:
            fps = get_framerate(self.loop_video.path)
            loop_video = standardize_video(self.loop_video.path)
        else:
            fps = 25

        loop_duration = duration
        for card in self.card_set.filter(duration__gt=0):
            loop_duration -= card.duration
            card_video = video_from_image(
                card.image.path, card.duration, fps=fps
            )
            (concat if card.order < 0 else outro).append(card_video)
            delete.append(card_video)

        if self.loop_video:
            loop_video_duration = get_duration(loop_video)
            times_loop = int(loop_duration // loop_video_duration)

            leftover_duration = loop_duration % loop_video_duration
            leftover = cut_video(loop_video, leftover_duration)
            concat.extend([loop_video] * times_loop + [leftover])
            delete.append(leftover)
        else:
            leftover = video_from_image(self.loop_card.path, loop_duration)
            concat.append(video_from_image(self.loop_card.path, loop_duration, fps=fps))
            delete.append(leftover)
        concat.extend(outro)

        output = concat_videos(concat)
        for p in delete:
            unlink(p)
        unlink(loop_video)
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
            data=thumbnail.getvalue(),
        )

    def prepare_thumbnail(self, audiobook):
        img = create_thumbnail(
            self.thumbnail_template.path,
            self.thumbnail_definition,
            {
                "author": ', '.join((a['name'] for a in audiobook.book['authors'])),
                "title": audiobook.book['title'],
            },
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
