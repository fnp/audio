from datetime import datetime
import os
import os.path
from urllib.parse import quote

from archive import settings
from django.contrib.auth.decorators import permission_required
from django.urls import reverse
from django.db.models import Q, Max
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import ListView

import mutagen

from archive.constants import status
from archive import models
from archive.forms import AudiobookForm
from archive import tasks
from archive.utils import all_files


def list_new(request):
    path = settings.NEW_PATH
    objects = sorted(all_files(path))
    return render(request, "archive/list_new.html", locals())


@permission_required('archive.change_audiobook')
def file_new(request, filename):
    filepath = filename
    root_filepath = os.path.join(settings.NEW_PATH, filename)
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
        form = AudiobookForm(initial=d)
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
def remove_to_archive(request, aid):
    """ move a managed file to the unmanaged files dir """

    audiobook = get_object_or_404(models.Audiobook, id=aid)
    old_path = audiobook.source_file.path
    new_path = os.path.join(settings.UNMANAGED_PATH,
        str(audiobook.source_file)[len(settings.FILES_SAVE_PATH):].lstrip('/'))
    new_dir = os.path.split(new_path)[0]
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)

    if not os.path.isfile(old_path):
        raise Http404

    success = False
    try_new_path = new_path
    try_number = 0
    while not success:
        try:
            os.link(old_path, try_new_path)
        except OSError:
            # destination file exists, don't overwrite it
            try_number += 1
            parts = new_path.rsplit('.', 1)
            parts[0] += '_%d' % try_number
            try_new_path = ".".join(parts)
        else:
            os.unlink(old_path)
            audiobook.delete()
            success = True

    return redirect(list_unmanaged)

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
def publish(request, aid, publish=True):
    """ mark file for publishing """
    audiobook = get_object_or_404(models.Audiobook, id=aid)
    tags = {
        'name': audiobook.title,
        'url': audiobook.url,
        'tags': audiobook.new_publish_tags(),
        }
    audiobook.set_mp3_tags(tags)
    audiobook.set_ogg_tags(tags)
    audiobook.mp3_status = audiobook.ogg_status = status.WAITING
    audiobook.save()
    # isn't there a race here?
    audiobook.mp3_task = tasks.Mp3Task.delay(request.user.id, aid, publish).task_id
    audiobook.ogg_task = tasks.OggTask.delay(request.user.id, aid, publish).task_id
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
    audiobook.youtube_status = None
    audiobook.youtube_queued = None
    audiobook.save()
    return redirect(file_managed, aid)


def download(request, aid, which="source"):
    if which not in ("source", "mp3", "ogg", 'mkv'):
        raise Http404
    audiobook = get_object_or_404(models.Audiobook, id=aid)
    field = which
    if which == 'mkv':
        field = 'youtube'
    file_ = getattr(audiobook, "%s_file" % field)
    if not file_:
        raise Http404
    ext = file_.path.rsplit('.', 1)[-1]
    response = HttpResponse(content_type='application/force-download')
    
    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s.%s" % (
        quote(audiobook.title.encode('utf-8'), safe=''), ext)
    with open(file_.path, 'rb') as f:
        response.write(f.read())
    #response['X-Sendfile'] = file_.path.encode('utf-8')
    return response


def list_publishing(request):
    objects = models.Audiobook.objects.exclude(
        mp3_status=None, ogg_status=None, youtube_status=None
    ).order_by("youtube_queued", "title")
    objects_by_status = {}
    for o in objects:
        statuses = set()
        if o.mp3_status:
            statuses.add((o.mp3_status, o.get_mp3_status_display()))
        if o.ogg_status:
            statuses.add((o.ogg_status, o.get_ogg_status_display()))
        if o.youtube_status:
            statuses.add((o.youtube_status, o.get_youtube_status_display()))
        for status in statuses:
            objects_by_status.setdefault(status, []).append(o)
    status_objects = sorted(objects_by_status.items(), reverse=True)

    return render(request, "archive/list_publishing.html", locals())


class AudiobookList(ListView):
    queryset = models.Audiobook.objects.all()


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

    tags = {}
    if audiobook.source_file:
        path = audiobook.source_file.path[len(settings.FILES_PATH):].lstrip('/')

        # for tags update
        tags = mutagen.File(audiobook.source_file.path.encode('utf-8'))
        if not tags:
            tags = {}
    form = AudiobookForm(instance=audiobook)

    user_can_publish = (
        request.user.is_authenticated and
        request.user.oauthconnection_set.filter(access=True).exists())

    alerts = []
    parts_count = audiobook.parts_count
    if parts_count > 1:
        series = models.Audiobook.objects.filter(slug=audiobook.slug)
        if not audiobook.index:
            alerts.append(_('There is more than one part, but index is not set.'))
        if set(series.values_list('index', flat=True)) != set(range(1, parts_count + 1)):
            alerts.append(_('Part indexes are not 1..%(parts_count)d.') % {"parts_count": parts_count})

    from youtube.models import YouTube
    youtube = YouTube.objects.first()
    youtube_title = youtube.get_title(audiobook)
    youtube_description = youtube.get_description(audiobook)

            
    return render(request, "archive/file_managed.html", locals())


def list_unmanaged(request):
    objects = sorted(all_files(settings.UNMANAGED_PATH))
    return render(request, "archive/list_unmanaged.html", locals())


def file_unmanaged(request, filename):
    tags = mutagen.File(os.path.join(settings.UNMANAGED_PATH, filename.encode('utf-8')))
    if not tags:
        tags = {}
    
    err_exists = request.GET.get('exists')
    return render(request, "archive/file_unmanaged.html", locals())


class BookView(ListView):
    template_name = 'archive/book.html'

    def get_queryset(self):
        return models.Audiobook.objects.filter(slug=self.kwargs["slug"]).order_by(
            "index"
        )
