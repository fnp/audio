from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from archive.constants import status
from archive.models import Audiobook
from . import tasks



@require_POST
@permission_required('archive.change_audiobook')
def publish(request, aid, publish=True):
    audiobook = get_object_or_404(Audiobook, id=aid)
    tags = {}
    #audiobook.set_youtube_tags(tags)
    audiobook.youtube_status = status.WAITING
    audiobook.save(update_fields=['youtube_status'])
    audiobook.youtube_task = tasks.YouTubeTask.delay(request.user.id, aid, publish).task_id
    audiobook.save(update_fields=['youtube_task'])
    return redirect(reverse('file', args=[aid]))
