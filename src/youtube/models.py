import io
from os import unlink
from tempfile import NamedTemporaryFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template import Template, Context
import requests
from apiclient import youtube_call
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


YOUTUBE_TITLE_LIMIT = 100


class YouTube(models.Model):
    name = models.CharField(max_length=255)
    title_template = models.CharField(max_length=1024, blank=True)
    description_template = models.TextField(blank=True)
    category = models.IntegerField(null=True, blank=True, choices=[
        (27, 'Edukacja'),
    ])
    intro_flac = models.FileField(upload_to='youtube/intro_flac', blank=True)
    outro_flac = models.FileField(upload_to='youtube/outro_flac', blank=True)
    loop_card = models.FileField(upload_to='youtube/card', blank=True)
    loop_video = models.FileField(upload_to='youtube/loop_video', blank=True)
    privacy_status = models.CharField(max_length=16, choices=[
        ('public', _('public')),
        ('unlisted', _('unlisted')),
        ('private', _('private')),
    ])
    genres = models.CharField(max_length=2048, blank=True)

    class Meta:
        verbose_name = _("YouTube configuration")
        verbose_name_plural = _("YouTube configurations")

    def __str__(self):
        return self.name

    def get_context(self, audiobook):
        return Context(dict(
            audiobook=audiobook,
        ))

    def get_description(self, audiobook):
        return Template(self.description_template).render(self.get_context(audiobook))

    def get_title(self, audiobook):
        return Template(self.title_template).render(self.get_context(audiobook))[:YOUTUBE_TITLE_LIMIT]

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

    def prepare_file(self, input_paths, output_path=None):
        audio = self.prepare_audio(input_paths)
        duration = self.get_duration(input_paths)
        video = self.prepare_video(duration)
        output = mux([video, audio], output_path=output_path)
        unlink(audio)
        unlink(video)
        return output

    def get_duration(self, input_paths):
        d = 0
        for input_path in input_paths:
            d += get_duration(input_path)
        if self.intro_flac:
            d += get_duration(self.intro_flac.path)
        if self.outro_flac:
            d += get_duration(self.outro_flac.path)
        return d

    def prepare_audio(self, input_paths):
        files = []
        if self.intro_flac:
            files.append(standardize_audio(self.intro_flac.path))
        for input_path in input_paths:
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
        if thumbnail is not None:
            response = youtube_call(
                "POST",
                "https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                params={'videoId': audiobook.youtube_id},
                data=thumbnail.getvalue(),
            )

    def prepare_thumbnail(self, audiobook):
        for thumbnail_template in ThumbnailTemplate.objects.filter(is_active=True).order_by('order'):
            if not thumbnail_template.is_for_audiobook(audiobook):
                continue
            thumbnail = thumbnail_template.generate(audiobook)
            if thumbnail is not None:
                return thumbnail


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


class ThumbnailTemplate(models.Model):
    youtube = models.ForeignKey(YouTube, models.CASCADE)
    order = models.SmallIntegerField()
    is_active = models.BooleanField()
    background = models.FileField(upload_to='youtube/thumbnail')
    definition = models.TextField()
    authors = models.CharField(max_length=255, blank=True)
    epochs = models.CharField(max_length=255, blank=True)
    kinds = models.CharField(max_length=255, blank=True)
    genres = models.CharField(max_length=255, blank=True)
    collections = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('order', )

    def generate(self, audiobook):
        try:
            title = audiobook.book['title']
            if audiobook.book.get('parent'):
                parent_title = audiobook.book['parent']['title']
                if not title.startswith(parent_title):
                    title = ", ".join((parent_title, title))

            img = create_thumbnail(
                self.background.path,
                self.definition,
                {
                    "author": ', '.join((a['name'] for a in audiobook.book['authors'])),
                    "title": title,
                    "part": (audiobook.youtube_volume or audiobook.part_name).strip(),
                },
                lambda name: Font.objects.get(name=name).truetype.path
            )
        except Exception as e:
            print(e)
            return
        else:
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return buf

    def is_for_audiobook(self, audiobook):
        for category in 'authors', 'epochs', 'kinds', 'genres':
            if getattr(self, category):
                book_slugs = set([g['slug'] for g in audiobook.book[category]])
                template_slugs = set([g.strip() for g in getattr(self, category).split(',')])
                if not book_slugs.intersection(template_slugs):
                    return False

        if self.collections:
            template_collections = set([g.strip() for g in self.collections.split(',')])
            in_any = False
            for collection in template_collections:
                apidata = requests.get(
                    f'https://wolnelektury.pl/api/collections/{collection}/'
                ).json()
                for book in apidata['books']:
                    if book['slug'] == audiobook.slug:
                        in_any = True
                        break
                if in_any:
                    break
            if not in_any:
                return False
        
        return True
