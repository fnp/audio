# Create your views here.

from datetime import datetime
import os
import os.path

from archive import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q, Max
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

import mutagen

from archive.constants import status
from archive import models
from archive.forms import AudiobookForm
from archive import tasks
from archive.utils import all_files


@login_required
def list_new(request):
    division = 'new'

    path = settings.NEW_PATH
    objects = sorted(all_files(path))
    return render(request, "archive/list_new.html", locals())


@permission_required('archive.change_audiobook')
def file_new(request, filename):
    division = 'new'

    filepath = filename.encode('utf-8')
    root_filepath = os.path.join(settings.NEW_PATH, filename.encode('utf-8'))
    if request.POST:
        form = AudiobookForm(request.POST)
        if form.is_valid():
            try:
                form.save(path=filepath)
            except IOError:
                raise Http404
            return redirect(list_new)

    try:
        tags = mutagen.File(root_filepath)
    except IOError:
        raise Http404
    d = {}
    if tags:
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
@permission_required('archive.change_audiobook')
def move_to_archive(request, filename):
    """ move a new file to the unmanaged files dir """

    filename_str = filename.encode('utf-8')
    old_path = os.path.join(settings.NEW_PATH, filename_str)
    new_path = os.path.join(settings.UNMANAGED_PATH, filename_str)
    new_dir = os.path.split(new_path)[0]
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)

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
@permission_required('archive.change_audiobook')
def move_to_new(request, filename):
    """ move a unmanaged file to new files dir """

    filename_str = filename.encode('utf-8')
    old_path = os.path.join(settings.UNMANAGED_PATH, filename_str)
    new_path = os.path.join(settings.NEW_PATH, filename_str)
    new_dir = os.path.split(new_path)[0]
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)

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
@permission_required('archive.change_audiobook')
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
@permission_required('archive.change_audiobook')
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
    objects_by_status = {}
    for o in objects:
        if o.mp3_status:
            k = o.mp3_status, o.get_mp3_status_display()
            objects_by_status.setdefault(k, []).append(o)
        if o.ogg_status and o.ogg_status != o.mp3_status:
            k = o.ogg_status, o.get_ogg_status_display()
            objects_by_status.setdefault(k, []).append(o)
    status_objects = sorted(objects_by_status.items(), reverse=True)

    return render(request, "archive/list_publishing.html", locals())


@login_required
def list_published(request):
    division = 'published'

    objects = models.Audiobook.objects.exclude(Q(mp3_published=None) | Q(ogg_published=None))
    return render(request, "archive/list_published.html", locals())


@permission_required('archive.change_audiobook')
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
    path = audiobook.source_file.path[len(settings.FILES_PATH):].lstrip('/')

    # for tags update
    tags = mutagen.File(audiobook.source_file.path)
    if not tags:
        tags = {}
    form = AudiobookForm(instance=audiobook)

    return render(request, "archive/file_managed.html", locals())


@login_required
def list_unmanaged(request):
    division = 'unmanaged'

    objects = sorted(all_files(settings.UNMANAGED_PATH))
    return render(request, "archive/list_unmanaged.html", locals())


@login_required
def file_unmanaged(request, filename):
    division = 'unmanaged'

    tags = mutagen.File(os.path.join(settings.UNMANAGED_PATH, filename.encode('utf-8')))
    if not tags:
        tags = {}
    
    err_exists = request.GET.get('exists')
    return render(request, "archive/file_unmanaged.html", locals())
