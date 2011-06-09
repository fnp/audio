from django.db import models
from jsonfield.fields import JSONField
from django.utils.translation import ugettext_lazy as _

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


class Audiobook(models.Model):
    source_file = models.FileField(upload_to='archive/files', verbose_name=_('source file'), editable=False)

    title = models.CharField(max_length=255, verbose_name=_('title'))
    artist = models.CharField(max_length=255, verbose_name=_('artist'))
    conductor = models.CharField(max_length=255, verbose_name=_('conductor'))
    encoded_by = models.CharField(max_length=255, verbose_name=_('encoded by'))
    date = models.CharField(max_length=255, verbose_name=_('date'))
    project = models.ForeignKey(Project, verbose_name=_('project'))
    url = models.URLField(max_length=255, verbose_name=_('book url'))
    modified = models.DateTimeField(null=True, editable=False)

    published_tags = JSONField(null=True, editable=False)
    mp3_file = models.FileField(null=True, upload_to='archive/final', editable=False)
    ogg_file = models.FileField(null=True, upload_to='archive/final', editable=False)
    publishing_tags = JSONField(null=True, editable=False)

    publish_wait = models.DateTimeField(null=True, editable=False) # somebody hit "publish"
    publishing = models.BooleanField(default=False, editable=False)
    published = models.DateTimeField(null=True, editable=False)

    class Meta:
        verbose_name = _("audiobook")
        verbose_name_plural = _("audiobooks")
        ordering = ("title",)

    def __unicode__(self):
        return self.title

    def new_publish_tags(self):
        return {
            'title': self.title,
            'copyright': 'Fundacja Nowoczesna Polska',
        }
