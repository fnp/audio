from unittest import mock
from django.test import TestCase
from archive.models import Audiobook
from . import tasks


@mock.patch("youtube.models.youtube_call")
@mock.patch("youtube.utils.subprocess")
@mock.patch("youtube.models.concat_audio")
@mock.patch("youtube.models.unlink")
@mock.patch("youtube.models.YouTube.prepare_thumbnail")
class YouTubeTests(TestCase):
    fixtures = ["tests.yaml"]

    def test_youtube_volumes(
        self, prepare_thumbnail, unlink, concat_audio, subprocess, youtube_call
    ):
        youtube_call.return_value = mock.Mock(
            json=mock.Mock(return_value={"id": "deadbeef"})
        )
        audiobooks = Audiobook.objects.all().order_by("index")

        self.assertEqual(audiobooks[0].youtube_volume_count, 3)
        self.assertEqual([a.youtube_volume_index for a in audiobooks], [1, 2, 2, 3])
        self.assertEqual(
            [a.is_youtube_publishable for a in audiobooks], [True, True, False, True]
        )

        tasks.YouTubeTask().run(None, 2, True)

        # In creating a volume of two audiobooks, we should've called concat with a list of two files.
        self.assertEqual(len(concat_audio.call_args[0][0]), 2)
