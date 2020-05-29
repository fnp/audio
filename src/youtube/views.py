from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
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
    audiobook.youtube_status = status.QUEUED
    audiobook.youtube_queued = now()
    audiobook.save(update_fields=['youtube_status', 'youtube_queued'])
    return redirect(reverse('file', args=[aid]))


def thumbnail(request, aid):
    audiobook = get_object_or_404(Audiobook, id=aid)
    yt = models.YouTube.objects.first()
    buf = yt.prepare_thumbnail(audiobook)
    return HttpResponse(buf.getvalue(), content_type='image/png')


class Preview(DetailView):
    model = Audiobook
    template_name = 'youtube/preview.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        yt = models.YouTube.objects.first()
        ctx['data'] = yt.get_data(ctx['object'])
        ctx['title'] = yt.get_title(ctx['object'])
        ctx['description'] = yt.get_description(ctx['object'])
        return ctx


@method_decorator(permission_required('archive.change_audiobook'), name='dispatch')
class Update(SingleObjectMixin, View):
    model = Audiobook

    def post(self, request, pk):
        yt = models.YouTube.objects.first()
        yt.update_data(self.get_object())
        return redirect(reverse('file', args=[pk]))
