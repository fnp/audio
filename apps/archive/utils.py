from hashlib import sha1
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile


class ExistingFile(UploadedFile):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        return super(ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass


class OverwriteStorage(FileSystemStorage):

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name


def sha1_file(f):
    sha = sha1()
    for piece in iter(lambda: f.read(1024*1024), ''):
        sha.update(piece)
    return sha.hexdigest()
