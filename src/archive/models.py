import io
import json
from os import unlink
import os.path
from urllib.parse import urljoin

from django.db import models
from time import sleep
from django.contrib.sites.models import Site
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_pglocks import advisory_lock
import requests
from archive.constants import status
from archive.settings import FILES_SAVE_PATH, ADVERT, ORGANIZATION, PROJECT
from archive.utils import OverwriteStorage, sha1_file
from youtube.utils import concat_audio, standardize_audio


class License(models.Model):
    uri = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Project(models.Model):
    """ an audiobook project, needed for specyfing sponsors """

    name = models.CharField(max_length=128, unique=True, db_index=True, verbose_name="Nazwa")
    sponsors = models.TextField(blank=True, null=True, verbose_name="Sponsorzy")
    description = models.TextField(blank=True, verbose_name="Opis")
    config = models.ForeignKey('Config', models.PROTECT)
    youtube = models.ForeignKey('youtube.YouTube', models.PROTECT)
    icon = models.FileField(upload_to='archive/project', blank=True, null=True)
    info_flac = models.FileField(upload_to='archive/info_flac', blank=True)

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_description(self):
        if self.description:
            return self.description
        return "Audiobook nagrany w ramach projektu %s%s." % (
            self.name,
            " finansowanego przez %s" % self.sponsors if self.sponsors else "",
        )

    def get_icon_url(self):
        if not self.icon:
            return ''
        return urljoin(
            'https://' + Site.objects.get_current().domain,
            self.icon.url
        )


class Config(models.Model):
    name = models.CharField(max_length=255)
    intro_flac = models.FileField(upload_to='config/intro_flac', blank=True)
    intro_min_seconds = models.IntegerField()
    outro_flac = models.FileField(upload_to='config/outro_flac', blank=True)
    outro_min_seconds = models.IntegerField()

    class Meta:
        verbose_name = _("Configuration")
        verbose_name_plural = _("Configurations")

    def __str__(self):
        return self.name

    def prepare_audio(self, audiobook):
        total_duration = audiobook.total_duration
        files = []
        if self.intro_flac and total_duration > self.intro_min_seconds and audiobook.is_first:
            files.append(standardize_audio(self.intro_flac.path))
        files.append(standardize_audio(audiobook.source_file.path))
        if self.outro_flac and total_duration > self.outro_min_seconds and audiobook.is_last:
            files.append(standardize_audio(self.outro_flac.path))
        output = concat_audio(files)
        for d in files:
            unlink(d)
        return output


def source_upload_to(intance, filename):
    return os.path.join(FILES_SAVE_PATH, filename) # FIXME: what about really long file names?


class Audiobook(models.Model):
    source_file = models.FileField(upload_to=source_upload_to, max_length=255, 
            verbose_name=_('source file'), editable=False)
    source_sha1 = models.CharField(max_length=40, editable=False)
    duration = models.FloatField(null=True, editable=False)

    title = models.CharField(max_length=255, verbose_name=_('title'))
    part_name = models.CharField(max_length=255, verbose_name=_('part name'), help_text=_('eg. chapter in a novel'),
                                 default='', blank=True)
    index = models.IntegerField(verbose_name=_('index'), default=0, help_text=_('Ordering of parts of a book.'))
    youtube_volume = models.CharField(
        _("Volume name for YouTube"),
        max_length=100,
        blank=True,
        help_text=_(
            "If set, audiobooks with the save value will be published as single YouTube video."
        ),
    )
    artist = models.CharField(max_length=255, verbose_name=_('artist'))
    conductor = models.CharField(max_length=255, verbose_name=_('conductor'))
    encoded_by = models.CharField(max_length=255, verbose_name=_('encoded by'))
    date = models.CharField(max_length=255, verbose_name=_('date'))
    project = models.ForeignKey(Project, models.PROTECT, verbose_name=_('project'))
    slug = models.SlugField(max_length=120, blank=True, help_text=_('WL catalogue slug of the book.'))
    translator = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('translator'))
    modified = models.DateTimeField(null=True, editable=False)
    license = models.ForeignKey(License, models.PROTECT, null=True, blank=True, verbose_name=_('license'))

    # publishing process
    mp3_status = models.SmallIntegerField(null=True, editable=False, choices=status.choices)
    mp3_task = models.CharField(max_length=64, null=True, editable=False)
    mp3_tags = models.TextField(null=True, editable=False)
    mp3_file = models.FileField(null=True, upload_to='archive/final', storage=OverwriteStorage(), editable=False)
    mp3_published_tags = models.TextField(null=True, editable=False)
    mp3_published = models.DateTimeField(null=True, editable=False)

    ogg_status = models.SmallIntegerField(null=True, editable=False, choices=status.choices)
    ogg_task = models.CharField(max_length=64, null=True, editable=False)
    ogg_tags = models.TextField(null=True, editable=False)
    ogg_file = models.FileField(null=True, upload_to='archive/final', storage=OverwriteStorage(), editable=False)
    ogg_published_tags = models.TextField(null=True, editable=False)
    ogg_published = models.DateTimeField(null=True, editable=False)

    youtube_status = models.SmallIntegerField(null=True, editable=False, choices=status.choices)
    youtube_task = models.CharField(max_length=64, null=True, editable=False)
    youtube_tags = models.TextField(null=True, editable=False)
    youtube_published_tags = models.TextField(null=True, editable=False)
    youtube_published = models.DateTimeField(null=True, editable=False)
    youtube_id = models.CharField(max_length=255, blank=True, default='')
    youtube_queued = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("audiobook")
        verbose_name_plural = _("audiobooks")
        ordering = ("title",)

    def __str__(self):
        return self.title

    @property
    def url(self):
        return f'https://wolnelektury.pl/katalog/lektura/{self.slug}/'

    @property
    def parts_count(self):
        return type(self).objects.filter(slug=self.slug).count()

    @property
    def total_duration(self):
        return type(self).objects.filter(slug=self.slug).aggregate(s=models.Sum('duration'))['s']

    @property
    def is_first(self):
        return not type(self).objects.filter(slug=self.slug, index__lte=self.index).exclude(pk=self.pk).exists()

    @property
    def is_last(self):
        return not type(self).objects.filter(slug=self.slug, index__gte=self.index).exclude(pk=self.pk).exists()
    
    @property
    def youtube_volume_count(self):
        total = 0
        prev_volume = None
        for a in type(self).objects.filter(slug=self.slug).order_by("index"):
            if not a.youtube_volume or a.youtube_volume != prev_volume:
                total += 1
            prev_volume = a.youtube_volume
        return total

    @property
    def youtube_volume_index(self):
        index = 0
        prev_volume = None
        for a in type(self).objects.filter(slug=self.slug, index__lte=self.index).order_by("index"):
            if not a.youtube_volume or a.youtube_volume != prev_volume:
                index += 1
            prev_volume = a.youtube_volume
        return index

    @property
    def is_youtube_publishable(self):
        return (
            not self.youtube_volume
            or not type(self)
            .objects.filter(youtube_volume=self.youtube_volume, index__lt=self.index)
            .exists()
        )

    def youtube_publish(self):
        if not self.is_youtube_publishable:
            return False
        self.youtube_status = status.QUEUED
        self.youtube_queued = now()
        self.save(update_fields=['youtube_status', 'youtube_queued'])

    def get_mp3_tags(self): return json.loads(self.mp3_tags) if self.mp3_tags else None
    def get_ogg_tags(self): return json.loads(self.ogg_tags) if self.ogg_tags else None
    def get_mp3_published_tags(self): return json.loads(self.mp3_published_tags) if self.mp3_published_tags else None
    def get_ogg_published_tags_tags(self): return json.loads(self.ogg_published_tags) if self.ogg_published_tags else None
    def set_mp3_tags(self, tags): self.mp3_tags = json.dumps(tags)
    def set_ogg_tags(self, tags): self.ogg_tags = json.dumps(tags)

    def published(self):
        return self.mp3_published and self.ogg_published

    def prepare_for_publish(self):
        tags = {
            'name': self.title,
            'url': self.url,
            'tags': self.new_publish_tags(),
        }
        self.set_mp3_tags(tags)
        self.set_ogg_tags(tags)
        self.mp3_status = self.ogg_status = status.WAITING
        self.save()
    
    def publish(self, user, publish=True):
        from . import tasks
        # isn't there a race here?
        self.mp3_task = tasks.Mp3Task.delay(user.id, self.pk, publish=publish).task_id
        self.ogg_task = tasks.OggTask.delay(user.id, self.pk, publish=publish).task_id
        self.save()

    def get_source_sha1(self):
        assert self.pk or self.source_sha1
        if not self.source_sha1:
            with advisory_lock(f'get_source_sha1_{self.pk}'):
                with open(self.source_file.path, 'rb') as f:
                    self.source_sha1 = sha1_file(f)
                self.save(update_fields=['source_sha1'])
        return self.source_sha1

    def new_publish_tags(self):
        title = self.title
        if self.translator:
            title += ' (tłum. %s)' % self.translator

        copyright = "%s %s." % (
                self.date, ORGANIZATION)
        if self.license:
            copyright += " Licensed to the public under %s verify at %s" % (
                self.license.uri, self.url)

        comment = "\n".join((
            self.project.get_description(),
            ADVERT
        ))

        tags = {
            'album': PROJECT,
            'albumartist': ORGANIZATION,
            'artist': self.artist,
            'comment': comment,
            'conductor': self.conductor,
            'contact': self.url,
            'copyright': copyright,
            'date': self.date,
            'genre': 'Speech',
            'language': 'pol',
            'organization': ORGANIZATION,
            'title': title,
            'project': self.project.name,
        }
        if self.license:
            tags['license'] = self.license.uri
        if self.project.sponsors:
            tags['funded_by'] = self.project.sponsors

        if self.source_sha1:
            tags['flac_sha1'] = self.source_sha1
        return tags

    def prepare_audio(self):
        return self.project.config.prepare_audio(self)
    
    @cached_property
    def book(self):
        if self.slug:
            apidata = requests.get(f'https://wolnelektury.pl/api/books/{self.slug}/').json()
        else:
            return {}
        return apidata

    @property
    def document(self):
        from librarian.document import WLDocument, parser
        from lxml import etree

        xml_url = self.book.get('xml', None)
        if xml_url is None:
            return None

        return WLDocument(
                etree.parse(
                    io.BytesIO(
                        requests.get(xml_url).content
                    )
                    ,parser = parser
                )
            )
