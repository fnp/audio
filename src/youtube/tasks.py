from archive.tasks import AudioFormatTask
from .models import YouTube


class YouTubeTask(AudioFormatTask):
    ext = 'mkv'
    prefix = 'youtube'

    def encode(self, in_path, out_path):
        YouTube.objects.first().prepare_file(in_path, out_path)

    def set_tags(self, audiobook, filename):
        pass

    @classmethod
    def save(cls, audiobook, file_name):
        """We do not save the video files."""
        pass

    def put(self, user, audiobook, filename):
        YouTube.objects.first().publish(audiobook, filename)
