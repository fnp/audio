from datetime import datetime
import errno
import mimetypes
import os
import os.path
import pipes
import subprocess
from tempfile import NamedTemporaryFile
from time import sleep

#from celery.decorators import task
from celery.task import Task
from fabric import api
from mutagen import File
from mutagen import id3

import mutagen

from archive.constants import status
from archive.models import Audiobook
from archive.settings import (BUILD_PATH, COVER_IMAGE,
    UPLOAD_HOST, UPLOAD_USER, UPLOAD_PATH, UPLOAD_CMD, UPLOAD_SUDO)
from archive.utils import ExistingFile

api.env.host_string = UPLOAD_HOST
api.env.user = UPLOAD_USER

class AudioFormatTask(Task):
    abstract = True

    @classmethod
    def set_status(cls, audiobook, status):
        setattr(audiobook, '%s_status' % cls.ext, status)
        audiobook.save()

    @staticmethod
    def encode(in_path, out_path):
        pass

    @classmethod
    def set_tags(cls, audiobook, file_name):
        audio = File(file_name)
        for k, v in getattr(audiobook, "%s_tags" % cls.ext)['tags'].items():
            audio[k] = v
        audio.save()

    @classmethod
    def save(cls, audiobook, file_name):
        getattr(audiobook, "%s_file" % cls.ext).save(
            "%d.%s" % (audiobook.pk, cls.ext),
            ExistingFile(file_name)
            )

    @classmethod
    def published(cls, audiobook):
        setattr(audiobook, "%s_published_tags" % cls.ext,
            getattr(audiobook, "%s_tags" % cls.ext))
        setattr(audiobook, "%s_tags" % cls.ext, None)
        setattr(audiobook, "%s_published" % cls.ext, datetime.now())
        cls.set_status(audiobook, None)

    @classmethod
    def put(cls, audiobook):
        tags = getattr(audiobook, "%s_tags" % cls.ext)
        prefix, slug = tags['url'].rstrip('/').rsplit('/', 1)
        name = tags['name']
        path = getattr(audiobook, "%s_file" % cls.ext).path
        api.put(path, UPLOAD_PATH)
        command = UPLOAD_CMD + (u' %s %s %s > output.txt' % (
            pipes.quote(os.path.join(UPLOAD_PATH, os.path.basename(path))),
            pipes.quote(slug),
            pipes.quote(name)
            )).encode('utf-8')
        print command
        if UPLOAD_SUDO:
            api.sudo(command, user=UPLOAD_SUDO, shell=False)
        else:
            api.run(command)

    def run(self, aid):
        audiobook = Audiobook.objects.get(id=aid)
        self.set_status(audiobook, status.ENCODING)

        try:
            os.makedirs(BUILD_PATH)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        out_file = NamedTemporaryFile(delete=False, prefix='audiobook-', suffix='.%s' % self.ext, dir=BUILD_PATH)
        out_file.close()
        self.encode(audiobook.source_file.path, out_file.name)
        self.set_status(audiobook, status.TAGGING)
        self.set_tags(audiobook, out_file.name)
        self.save(audiobook, out_file.name)
        self.set_status(audiobook, status.SENDING)

        #self.put(audiobook)

        self.published(audiobook)
        audiobook.save()


class Mp3Task(AudioFormatTask):
    ext = 'mp3'

    # these shouldn't be staticmethods
    def id3_text(tag, text):
        return tag(encoding=1, text=text)
    def id3_url(tag, text):
        return tag(url=text)
    def id3_comment(tag, text, lang=u'pol'):
        return tag(encoding=1, lang=lang, desc=u'', text=text)
    def id3_sha1(tag, text, what=u''):
        return tag(owner='http://wolnelektury.pl?%s' % what, data=text)

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
        'flac_sha1': (id3_sha1, id3.PRIV, 'flac_sha1'),
    }

    @staticmethod
    def encode(in_path, out_path):
        # 44.1kHz 64kbps mono MP3
        subprocess.check_call(['ffmpeg', 
            '-i', in_path,
            '-ar', '44100',
            '-ab', '64k',
            '-ac', '1',
            '-y',
            out_path
            ])

    @classmethod
    def set_tags(cls, audiobook, file_name):
        audio = id3.ID3(file_name)
        for k, v in audiobook.mp3_tags['tags'].items():
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
        subprocess.check_call(['oggenc', 
            in_path,
            '--discard-comments',
            '--resample', '44100',
            '--downmix',
            '-b', '64',
            '-o', out_path
            ])
