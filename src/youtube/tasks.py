import os
from archive.tasks import AudioFormatTask
from .models import YouTube


class YouTubeTask(AudioFormatTask):
    ext = 'mkv'
    prefix = 'youtube'

    def encode(self, in_paths, out_path):
        self.audiobook.project.youtube.prepare_file(in_paths, out_path)

    def set_tags(self, audiobook, filename):
        pass

    @classmethod
    def save(cls, audiobook, file_name):
        """We do not save the video files."""
        os.unlink(file_name)

    def put(self, user, audiobook, filename):
        audiobook.project.youtube.publish(audiobook, filename)

    def get_source_file_paths(self, audiobook):
        if not audiobook.youtube_volume:
            paths = [audiobook.source_file.path]
        else:
            paths = [
                a.source_file.path
                for a in type(audiobook)
                .objects.filter(
                    slug=audiobook.slug, youtube_volume=audiobook.youtube_volume
                )
                .order_by("index")
            ]
        if audiobook.project.info_flac:
            paths.append(audiobook.project.info_flac.path)
        return paths
