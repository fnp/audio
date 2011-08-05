from hashlib import sha1
from django.core.files.uploadedfile import UploadedFile


class ExistingFile(UploadedFile):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        return super(ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass


def sha1_file(f):
    sha = sha1()
    for piece in iter(lambda: f.read(1024*1024), ''):
        sha.update(piece)
    return sha.hexdigest()
