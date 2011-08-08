# Create your views here.

from datetime import datetime
import os
import os.path

from archive import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q, Max
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST

import mutagen

from archive.constants import status
from archive import models
from archive.forms import AudiobookForm
from archive import tasks


@login_required
def list_new(request):
    division = 'new'

    path = settings.NEW_PATH
    objects = sorted(os.listdir(path))
    return render(request, "archive/list_new.html", locals())


@login_required
def file_new(request, filename):
    division = 'new'

    filepath = os.path.join(settings.NEW_PATH, filename.encode('utf-8'))
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
@login_required
def move_to_archive(request, filename):
    """ move a new file to the unmanaged files dir """

    filename_str = filename.encode('utf-8')
    old_path = os.path.join(settings.NEW_PATH, filename_str)
    if not os.path.isdir(settings.UNMANAGED_PATH):
        os.makedirs(settings.UNMANAGED_PATH)
    new_path = os.path.join(settings.UNMANAGED_PATH, filename_str)

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
@login_required
def move_to_new(request, filename):
    """ move a unmanaged file to new files dir """

    filename_str = filename.encode('utf-8')
    old_path = os.path.join(settings.UNMANAGED_PATH, filename_str)
    if not os.path.isdir(settings.NEW_PATH):
        os.makedirs(settings.NEW_PATH)
    new_path = os.path.join(settings.NEW_PATH, filename_str)

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
@login_required
def publish(request, aid):
    """ mark file for publishing """
    audiobook = get_object_or_404(models.Audiobook, id=aid)
    tags = {
        'name': audiobook.title,
        'url': audiobook.url,
        'tags': audiobook.new_publish_tags(),
        }
    audiobook.mp3_tags = tags
    audiobook.ogg_tags = tags
    audiobook.mp3_status = audiobook.ogg_status = status.WAITING
    audiobook.save()
    # isn't there a race here?
    audiobook.mp3_task = tasks.Mp3Task.delay(aid).task_id
    audiobook.ogg_task = tasks.OggTask.delay(aid).task_id
    audiobook.save()

    return redirect(file_managed, aid)


@require_POST
@login_required
def cancel_publishing(request, aid):
    """ cancel scheduled publishing """
    audiobook = get_object_or_404(models.Audiobook, id=aid)
    # TODO: cancel tasks
    audiobook.mp3_status = None
    audiobook.ogg_status = None
    audiobook.save()
    return redirect(file_managed, aid)


@login_required
def list_unpublished(request):
    division = 'unpublished'

    objects = models.Audiobook.objects.filter(Q(mp3_published=None) | Q(ogg_published=None))
    return render(request, "archive/list_unpublished.html", locals())


@login_required
def list_publishing(request):
    division = 'publishing'

    objects = models.Audiobook.objects.exclude(mp3_status=None, ogg_status=None)
    objects_by_status = SortedDict()
    for o in objects:
        if o.mp3_status:
            k = o.mp3_status, o.get_mp3_status_display()
            objects_by_status.setdefault(k, []).append(o)
        if o.ogg_status and o.ogg_status != o.mp3_status:
            k = o.ogg_status, o.get_ogg_status_display()
            objects_by_status.setdefault(k, []).append(o)

    return render(request, "archive/list_publishing.html", locals())


@login_required
def list_published(request):
    division = 'published'

    objects = models.Audiobook.objects.exclude(Q(mp3_published=None) | Q(ogg_published=None))
    return render(request, "archive/list_published.html", locals())


@login_required
def file_managed(request, id):
    audiobook = get_object_or_404(models.Audiobook, id=id)

    if request.POST:
        form = AudiobookForm(request.POST, instance=audiobook)
        if form.is_valid():
            try:
                form.save()
            except IOError:
                raise Http404

    division = 'published' if audiobook.published() else 'unpublished'

    # for tags update
    tags = mutagen.File(audiobook.source_file.path)
    form = AudiobookForm(instance=audiobook)

    return render(request, "archive/file_managed.html", locals())


@login_required
def list_unmanaged(request):
    division = 'unmanaged'

    objects = sorted(os.listdir(settings.UNMANAGED_PATH))
    return render(request, "archive/list_unmanaged.html", locals())


@login_required
def file_unmanaged(request, filename):
    division = 'unmanaged'

    tags = mutagen.File(os.path.join(settings.UNMANAGED_PATH, filename.encode('utf-8')))
    err_exists = request.GET.get('exists')
    return render(request, "archive/file_unmanaged.html", locals())


@login_required
def logout_view(request):
    logout(request)
    return redirect(list_new)
