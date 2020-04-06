from archive.tasks import AudioFormatTask
from .models import YouTube


class YouTubeTask(AudioFormatTask):
    ext = 'mkv'
    prefix = 'youtube'

    def encode(self, in_path, out_path):
        YouTube.objects.first().prepare_file(in_path, out_path)

    def set_tags(self, audiobook, filename):
        pass

    def put(self, user, audiobook, filename):
        YouTube.objects.first().publish(audiobook, filename)
