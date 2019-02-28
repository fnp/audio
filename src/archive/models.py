# -*- coding: utf-8 -*-
import os.path

from django.db import models
from time import sleep
from jsonfield.fields import JSONField
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _
from archive.constants import status
from archive.settings import FILES_SAVE_PATH, ADVERT, LICENSE, ORGANIZATION, PROJECT
from archive.utils import OverwriteStorage, sha1_file

# Create your models here.


class Project(models.Model):
    """ an audiobook project, needed for specyfing sponsors """

    name = models.CharField(max_length=128, unique=True, db_index=True, verbose_name="Nazwa")
    sponsors = models.TextField(blank=True, null=True, verbose_name="Sponsorzy")

    class Meta:
        verbose_name = _("project")
        verbose_name_plural = _("projects")
        ordering = ("name",)

    def __unicode__(self):
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
    project = models.ForeignKey(Project, verbose_name=_('project'))
    url = models.URLField(max_length=255, verbose_name=_('book url'))
    translator = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('translator'))
    modified = models.DateTimeField(null=True, editable=False)

    # publishing process
    mp3_status = models.SmallIntegerField(null=True, editable=False, choices=status.choices)
    mp3_task = models.CharField(max_length=64, null=True, editable=False)
    mp3_tags = JSONField(null=True, editable=False)
    mp3_file = models.FileField(null=True, upload_to='archive/final', storage=OverwriteStorage(), editable=False)
    mp3_published_tags = JSONField(null=True, editable=False)
    mp3_published = models.DateTimeField(null=True, editable=False)

    ogg_status = models.SmallIntegerField(null=True, editable=False, choices=status.choices)
    ogg_task = models.CharField(max_length=64, null=True, editable=False)
    ogg_tags = JSONField(null=True, editable=False)
    ogg_file = models.FileField(null=True, upload_to='archive/final', storage=OverwriteStorage(), editable=False)
    ogg_published_tags = JSONField(null=True, editable=False)
    ogg_published = models.DateTimeField(null=True, editable=False)


    class Meta:
        verbose_name = _("audiobook")
        verbose_name_plural = _("audiobooks")
        ordering = ("title",)

    def __unicode__(self):
        return self.title

    def published(self):
        return self.mp3_published and self.ogg_published

    def get_source_sha1(self):
        source_sha1 = self.source_sha1
        if self.pk:
            source_sha1 = type(self).objects.get(pk=self.pk).source_sha1
            while source_sha1 == 'wait':
                sleep(10)
        if not source_sha1:
            self.source_sha1 = 'wait'
            if self.pk:
                type(self).objects.filter(pk=self.pk).update(source_sha1='wait')
            try:
                f = open(force_bytes(self.source_file.path))
                source_sha1 = sha1_file(f)
                self.source_sha1 = source_sha1
                if self.pk:
                    type(self).objects.filter(pk=self.pk).update(source_sha1=source_sha1)
            except:
                self.source_sha1 = ''
                if self.pk:
                    type(self).objects.filter(pk=self.pk).update(source_sha1='')
                return None
        return source_sha1


    def new_publish_tags(self):
        title = self.title
        if self.translator:
            title += u' (tłum. %s)' % self.translator

        copyright = u"%s %s. Licensed to the public under %s verify at %s" % (
                self.date, ORGANIZATION, LICENSE, self.url)

        comment = u"Audiobook nagrany w ramach projektu %s%s.\n%s" % (
                    self.project.name,
                    u" finansowanego przez %s" % self.project.sponsors if self.project.sponsors else "",
                    ADVERT)

        tags = {
            'album': PROJECT,
            'albumartist': ORGANIZATION,
            'artist': self.artist,
            'comment': comment,
            'conductor': self.conductor,
            'contact': self.url,
            'copyright': copyright,
            'date': self.date,
            'genre': u'Speech',
            'language': u'pol',
            'license': LICENSE,
            'organization': ORGANIZATION,
            'title': title,
            #'flac_sha1': self.get_source_sha1(),
            'project': self.project.name,
            'funded_by': self.project.sponsors,
        }
        if self.source_sha1 and self.source_sha1 != 'wait':
            tags['flac_sha1'] = self.source_sha1
        return tags
