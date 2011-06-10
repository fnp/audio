import os.path
from django.conf import settings

# this is where the end user puts new files
try:
    NEW_PATH = settings.ARCHIVE_NEW_PATH
except AttributeError:
    NEW_PATH = os.path.abspath(os.path.join(settings.MEDIA_ROOT,
                        "archive/new"))

# here the application keeps its managed files
try:
    FILES_PATH = settings.ARCHIVE_FILES_PATH
except AttributeError:
    FILES_PATH = os.path.abspath(os.path.join(settings.MEDIA_ROOT,
                        "archive/files"))


# here the app keeps the unmanaged (archive) files
try:
    UNMANAGED_PATH = settings.ARCHIVE_UNMANAGED_PATH
except AttributeError:
    UNMANAGED_PATH = os.path.abspath(os.path.join(settings.MEDIA_ROOT,
                        "archive/unmanaged"))


# here the app keeps the resulting (published) files
try:
    FINAL_PATH = settings.ARCHIVE_FINAL_PATH
except AttributeError:
    FINAL_PATH = os.path.abspath(os.path.join(settings.MEDIA_ROOT,
                        "archive/final"))
