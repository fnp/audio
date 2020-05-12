import json
import os.path

from django.db import models
from time import sleep
from django.utils.translation import gettext_lazy as _
from django_pglocks import advisory_lock
from archive.constants import status
from archive.settings import FILES_SAVE_PATH, ADVERT, LICENSE, ORGANIZATION, PROJECT
from archive.utils import OverwriteStorage, sha1_file


class Project(models.Model):
    """ an audiobook project, needed for specyfing sponsors """

    name = models.CharField(max_length=128, unique=True, db_index=True, verbose_name="Nazwa")
    sponsors = models.TextField(blank=True, null=True, verbose_name="Sponsorzy")
    description = models.TextField(blank=True, verbose_name="Opis")

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


class Piece(models.Model):
    name = models.CharField(max_length=255)
    source_file = models.FileField(upload_to='piece')
    is_outro = models.BooleanField(default=False)
    min_audiobook_duration = models.IntegerField(default=0)

    def __str__(self):
        return self.name


def source_upload_to(intance, filename):
    return os.path.join(FILES_SAVE_PATH, filename) # FIXME: what about really long file names?


class Audiobook(models.Model):
    source_file = models.FileField(upload_to=source_upload_to, max_length=255, 
            verbose_name=_('source file'), editable=False)
    source_sha1 = models.CharField(max_length=40, editable=False)

    title = models.CharField(max_length=255, verbose_name=_('title'))
    part_name = models.CharField(max_length=255, verbose_name=_('part name'), help_text=_('eg. chapter in a novel'),
                                 default='', blank=True)
    index = models.IntegerField(verbose_name=_('index'), default=0)
    parts_count = models.IntegerField(verbose_name=_('parts count'), default=1)
    artist = models.CharField(max_length=255, verbose_name=_('artist'))
    conductor = models.CharField(max_length=255, verbose_name=_('conductor'))
    encoded_by = models.CharField(max_length=255, verbose_name=_('encoded by'))
    date = models.CharField(max_length=255, verbose_name=_('date'))
    project = models.ForeignKey(Project, models.PROTECT, verbose_name=_('project'))
    url = models.URLField(max_length=255, verbose_name=_('book url'))
    translator = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('translator'))
    modified = models.DateTimeField(null=True, editable=False)

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
    youtube_file = models.FileField(null=True, upload_to='archive/final', storage=OverwriteStorage(), editable=False)
    youtube_published_tags = models.TextField(null=True, editable=False)
    youtube_published = models.DateTimeField(null=True, editable=False)
    youtube_id = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = _("audiobook")
        verbose_name_plural = _("audiobooks")
        ordering = ("title",)

    def __str__(self):
        return self.title

    def get_mp3_tags(self): return json.loads(self.mp3_tags) if self.mp3_tags else None
    def get_ogg_tags(self): return json.loads(self.ogg_tags) if self.ogg_tags else None
    def get_mp3_published_tags(self): return json.loads(self.mp3_published_tags) if self.mp3_published_tags else None
    def get_ogg_published_tags_tags(self): return json.loads(self.ogg_published_tags) if self.ogg_published_tags else None
    def set_mp3_tags(self, tags): self.mp3_tags = json.dumps(tags)
    def set_ogg_tags(self, tags): self.ogg_tags = json.dumps(tags)

    def published(self):
        return self.mp3_published and self.ogg_published

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

        copyright = "%s %s. Licensed to the public under %s verify at %s" % (
                self.date, ORGANIZATION, LICENSE, self.url)

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
            'license': LICENSE,
            'organization': ORGANIZATION,
            'title': title,
            'project': self.project.name,
        }
        if self.project.sponsors:
            tags['funded_by'] = self.project.sponsors

        if self.source_sha1:
            tags['flac_sha1'] = self.source_sha1
        return tags

