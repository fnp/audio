from django.core.management.base import BaseCommand
from archive.constants import status
from archive.models import Audiobook
from youtube import tasks


class Command(BaseCommand):
    help = "Schedules some audiobooks for uploading to YouTube."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=6)

    def handle(self, *args, **options):
        for audiobook in (
            Audiobook.objects.filter(status=status.QUEUED)
            .exclude(youtube_queued=None)
            .order_by("youtube_queued")[: options["limit"]]
        ):
            audiobook.youtube_task = tasks.YouTubeTask.delay(
                None, audiobook.id, True
            ).task_id
            audiobook.youtube_status = status.WAITING
            audiobook.save(update_fields=["youtube_task", "youtube_status"])
