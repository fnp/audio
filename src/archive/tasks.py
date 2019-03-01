from datetime import datetime
import errno
import mimetypes
import os
import os.path
import pipes
import stat
import subprocess
from tempfile import NamedTemporaryFile
from time import sleep

from celery.task import Task
from django.db.models import F
from django.contrib.auth.models import User
from mutagen import File
from mutagen import id3

from apiclient import api_call
from archive.constants import status
from archive.models import Audiobook
from archive.settings import BUILD_PATH, COVER_IMAGE, UPLOAD_URL
from archive.utils import ExistingFile


class AudioFormatTask(Task):
    abstract = True

    class RemoteOperationError(BaseException):
        pass

    @classmethod
    def set_status(cls, aid, status):
        Audiobook.objects.filter(pk=aid).update(
            **{'%s_status' % cls.ext: status})

    @staticmethod
    def encode(in_path, out_path):
        raise NotImplemented

    @classmethod
    def set_tags(cls, audiobook, file_name):
        tags = getattr(audiobook, "%s_tags" % cls.ext)['tags']
        if not tags.get('flac_sha1'):
            tags['flac_sha1'] = audiobook.get_source_sha1()
        audio = File(file_name)
        for k, v in tags.items():
            audio[k] = v
        audio.save()

    @classmethod
    def save(cls, audiobook, file_name):
        field = "%s_file" % cls.ext
        getattr(audiobook, field).save(
            "%d.%s" % (audiobook.pk, cls.ext),
            ExistingFile(file_name),
            save=False
            )
        os.chmod(getattr(audiobook, field).path, stat.S_IREAD|stat.S_IWRITE|stat.S_IRGRP|stat.S_IROTH)
        Audiobook.objects.filter(pk=audiobook.pk).update(
            **{field: getattr(audiobook, field)})

    @classmethod
    def published(cls, aid):
        kwargs = {
            "%s_published_tags" % cls.ext: F("%s_tags" % cls.ext),
            "%s_tags" % cls.ext: None,
            "%s_published" % cls.ext: datetime.now(),
            '%s_status' % cls.ext: None,
        }
        Audiobook.objects.filter(pk=aid).update(**kwargs)

    @classmethod
    def put(cls, user, audiobook, path):
        tags = getattr(audiobook, "%s_tags" % cls.ext)
        data = {
            'book': tags['url'],
            'type': cls.ext,
            'name': tags['name'],
            'part_name': audiobook.part_name,
            'part_index': audiobook.index,
            'parts_count': audiobook.parts_count,
            'source_sha1': audiobook.source_sha1,
        }
        api_call(user, UPLOAD_URL, data=data, files={
            "file": open(path, 'rb'),
        })

    def run(self, uid, aid, publish=True):
        aid = int(aid)
        audiobook = Audiobook.objects.get(id=aid)
        self.set_status(aid, status.ENCODING)

        user = User.objects.get(id=uid)

        try:
            os.makedirs(BUILD_PATH)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        out_file = NamedTemporaryFile(delete=False, prefix='%d-' % aid, suffix='.%s' % self.ext, dir=BUILD_PATH)
        out_file.close()
        self.encode(audiobook.source_file.path, out_file.name)
        self.set_status(aid, status.TAGGING)
        self.set_tags(audiobook, out_file.name)
        self.set_status(aid, status.SENDING)

        if publish:
            self.put(user, audiobook, out_file.name)
            self.published(aid)
        else:
            self.set_status(aid, None)

        self.save(audiobook, out_file.name)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        aid = (args[0], kwargs.get('aid'))[0]
        self.set_status(aid, None)


class Mp3Task(AudioFormatTask):
    ext = 'mp3'

    # these shouldn't be staticmethods
    def id3_text(tag, text):
        return tag(encoding=1, text=text)
    def id3_url(tag, text):
        return tag(url=text)
    def id3_comment(tag, text, lang=u'pol'):
        return tag(encoding=1, lang=lang, desc=u'', text=text)
    def id3_priv(tag, text, what=u''):
        return tag(owner='wolnelektury.pl?%s' % what, data=text.encode('utf-8'))

    TAG_MAP = {
        'album': (id3_text, id3.TALB),
        'albumartist': (id3_text, id3.TPE2),
        'artist': (id3_text, id3.TPE1),
        'conductor': (id3_text, id3.TPE3),
        'copyright': (id3_text, id3.TCOP),
        'date': (id3_text, id3.TDRC),
        'genre': (id3_text, id3.TCON),
        'language': (id3_text, id3.TLAN),
        'organization': (id3_text, id3.TPUB),
        'title': (id3_text, id3.TIT2),
        'comment': (id3_comment, id3.COMM, 'pol'),
        'contact': (id3_url, id3.WOAF),
        'license': (id3_url, id3.WCOP),
        'flac_sha1': (id3_priv, id3.PRIV, 'flac_sha1'),
        'project': (id3_priv, id3.PRIV, 'project'),
        'funded_by': (id3_priv, id3.PRIV, 'funded_by'),
    }

    @staticmethod
    def encode(in_path, out_path):
        # 44.1kHz 64kbps mono MP3
        subprocess.check_call(['ffmpeg', 
            '-i', in_path.encode('utf-8'),
            '-ar', '44100',
            '-ab', '64k',
            '-ac', '1',
            '-y',
            '-acodec', 'libmp3lame',
            out_path.encode('utf-8')
            ])

    @classmethod
    def set_tags(cls, audiobook, file_name):
        mp3_tags = audiobook.mp3_tags['tags']
        if not mp3_tags.get('flac_sha1'):
            mp3_tags['flac_sha1'] = audiobook.get_source_sha1()
        audio = id3.ID3(file_name)
        for k, v in mp3_tags.items():
            factory_tuple = cls.TAG_MAP[k]
            factory, tagtype = factory_tuple[:2]
            audio.add(factory(tagtype, v, *factory_tuple[2:]))

        if COVER_IMAGE:
            mime = mimetypes.guess_type(COVER_IMAGE)
            f = open(COVER_IMAGE)
            audio.add(id3.APIC(encoding=0, mime=mime, type=3, desc=u'', data=f.read()))
            f.close()

        audio.save()


class OggTask(AudioFormatTask):
    ext = 'ogg'

    @staticmethod
    def encode(in_path, out_path):
        # 44.1kHz 64kbps mono Ogg Vorbis
        subprocess.check_call(['ffmpeg', 
            '-i', in_path.encode('utf-8'),
            '-ar', '44100',
            '-ab', '64k',
            '-ac', '1',
            '-y',
            '-acodec', 'libvorbis',
            out_path.encode('utf-8')
            ])
