# Create your views here.

from datetime import datetime
import os
import os.path

from archive import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

import mutagen

from archive import models
from archive.forms import AudiobookForm


def list_new(request):
    division = 'new'

    path = settings.NEW_PATH
    objects = sorted(os.listdir(path))
    return render(request, "archive/list_new.html", locals())


def file_new(request, filename):
    division = 'new'

    filepath = os.path.join(settings.NEW_PATH, filename)
    if request.POST:
        form = AudiobookForm(request.POST)
        if form.is_valid():
            try:
                form.save(path=filepath)
            except IOError:
                raise Http404
            return redirect(list_new)

    try:
        tags = mutagen.File(filepath)
    except IOError:
        raise Http404
    d = {}
    for tag in tags:
        value = tags[tag]
        if isinstance(value, list):
            d[tag] = value[0]
        else:
            d[tag] = value
        if tag == 'project':
            try:
                d[tag] = models.Project.objects.get(name=d[tag]).pk
            except models.Project.DoesNotExist:
                d[tag] = None

    if not request.POST:
        form = AudiobookForm(d)
    return render(request, "archive/file_new.html", locals())


@require_POST
def move_to_archive(request, filename):
    """ move a new file to the unmanaged files dir """

    old_path = os.path.join(settings.NEW_PATH, filename)
    if not os.path.isdir(settings.UNMANAGED_PATH):
        os.makedirs(settings.UNMANAGED_PATH)
    new_path = os.path.join(settings.UNMANAGED_PATH, filename)

    if not os.path.isfile(old_path):
        raise Http404

    try:
        os.link(old_path, new_path)
        os.unlink(old_path)
    except OSError:
        # destination file exists, don't overwrite it
        # TODO: this should probably be more informative
        return redirect(file_new, filename)

    return redirect(list_new)


@require_POST
def move_to_new(request, filename):
    """ move a unmanaged file to new files dir """

    old_path = os.path.join(settings.UNMANAGED_PATH, filename)
    if not os.path.isdir(settings.NEW_PATH):
        os.makedirs(settings.NEW_PATH)
    new_path = os.path.join(settings.NEW_PATH, filename)

    if not os.path.isfile(old_path):
        raise Http404

    try:
        os.link(old_path, new_path)
        os.unlink(old_path)
    except OSError:
        # destination file exists, don't overwrite it
        # TODO: this should probably be more informative
        return redirect(reverse(file_unmanaged, args=[filename]) + "?exists=1")

    return redirect(list_unmanaged)

@require_POST
def publish(request, id):
    """ mark file for publishing """
    audiobook = get_object_or_404(models.Audiobook, id=id)
    audiobook.publish_wait = datetime.now()
    audiobook.publishing_tags = audiobook.new_publish_tags()
    audiobook.save()
    return redirect(file_managed, id)

@require_POST
def cancel_publishing(request, id):
    """ cancel scheduled publishing """
    audiobook = get_object_or_404(models.Audiobook, id=id)
    if not audiobook.publishing:
        audiobook.publish_wait = None
        audiobook.publishing_tags = None
        audiobook.save()
    return redirect(file_managed, id)


def list_unpublished(request):
    division = 'unpublished'

    objects = models.Audiobook.objects.filter(published=None)
    return render(request, "archive/list_unpublished.html", locals())



def file_managed(request, id):
    audiobook = get_object_or_404(models.Audiobook, id=id)
    division = 'published' if audiobook.published else 'unpublished'

    # for tags update
    tags = mutagen.File(audiobook.source_file.path)
    form = AudiobookForm(instance=audiobook)

    return render(request, "archive/file_managed.html", locals())



def list_published(request):
    division = 'published'

    objects = models.Audiobook.objects.exclude(published=None)
    return render(request, "archive/list_published.html", locals())




def list_unmanaged(request):
    division = 'unmanaged'

    objects = sorted(os.listdir(settings.UNMANAGED_PATH))
    return render(request, "archive/list_unmanaged.html", locals())


def file_unmanaged(request, filename):
    division = 'unmanaged'

    tags = mutagen.File(os.path.join(settings.UNMANAGED_PATH, filename))
    err_exists = request.GET.get('exists')
    return render(request, "archive/file_unmanaged.html", locals())

