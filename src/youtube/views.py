from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from archive.constants import status
from archive.models import Audiobook
from . import models, tasks



@require_POST
@permission_required('archive.change_audiobook')
def publish(request, aid, publish=True):
    audiobook = get_object_or_404(Audiobook, id=aid)
    if audiobook.is_youtube_publishable:
        audiobook.youtube_publish()
    return redirect(reverse('file', args=[aid]))


@require_POST
@permission_required('archive.change_audiobook')
def book_publish(request, slug):
    for audiobook in Audiobook.objects.filter(slug=slug).order_by("index"):
        if audiobook.is_youtube_publishable:
            audiobook.youtube_publish()
    return redirect(reverse('book', args=[slug]))


def thumbnail(request, aid, thumbnail_id=None):
    audiobook = get_object_or_404(Audiobook, id=aid)
    if thumbnail_id is None:
        yt = audiobook.project.youtube
        buf = yt.prepare_thumbnail(audiobook)
    else:
        template = get_object_or_404(models.ThumbnailTemplate, id=thumbnail_id)
        buf = template.generate(audiobook)
    buf = buf.getvalue() if buf is not None else b''
    return HttpResponse(buf, content_type='image/png')


class Preview(DetailView):
    model = Audiobook
    template_name = 'youtube/preview.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        yt = ctx['object'].project.youtube
        ctx['data'] = yt.get_data(ctx['object'])
        ctx['title'] = yt.get_title(ctx['object'])
        ctx['description'] = yt.get_description(ctx['object'])
        ctx['templates'] = models.ThumbnailTemplate.objects.all()
        return ctx


@method_decorator(permission_required('archive.change_audiobook'), name='dispatch')
class Update(SingleObjectMixin, View):
    model = Audiobook

    def post(self, request, pk):
        obj = self.get_object()
        yt = obj.project.youtube
        yt.update_data(obj)
        return redirect(reverse('file', args=[pk]))


@method_decorator(permission_required('archive.change_audiobook'), name='dispatch')
class UpdateThumbnail(SingleObjectMixin, View):
    model = Audiobook

    def post(self, request, pk):
        obj = self.get_object()
        yt = obj.project.youtube
        yt.update_thumbnail(obj)
        return redirect(reverse('file', args=[pk]))
