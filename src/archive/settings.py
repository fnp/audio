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

_media_root = os.path.abspath(settings.MEDIA_ROOT)
if FILES_PATH.startswith(_media_root):
    FILES_SAVE_PATH = FILES_PATH[len(_media_root):].lstrip('/')


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


# here the app keeps temporary build files
try:
    BUILD_PATH = settings.ARCHIVE_BUILD_PATH
except AttributeError:
    BUILD_PATH = os.path.abspath(os.path.join(settings.MEDIA_ROOT,
                        "archive/build"))

UPLOAD_URL = getattr(
    settings,
    'ARCHIVE_UPLOAD_URL',
    'audiobooks/'
)


try:
    PROJECT = settings.ARCHIVE_PROJECT
except AttributeError:
    PROJECT = 'Wolne Lektury'

try:
    LICENSE = settings.ARCHIVE_LICENSE
except AttributeError:
    LICENSE = 'http://creativecommons.org/licenses/by-sa/3.0/deed.pl'

try:
    ORGANIZATION = settings.ARCHIVE_ORGANIZATION
except AttributeError:
    ORGANIZATION = 'Fundacja Nowoczesna Polska'

try:
    ADVERT = settings.ARCHIVE_ADVERT
except AttributeError:
    ADVERT = """
Przekaż 1% podatku na rozwój Wolnych Lektur:
Fundacja Nowoczesna Polska
KRS 0000070056
http://nowoczesnapolska.org.pl/wesprzyj_nas/
"""

try:
    COVER_IMAGE = settings.ARCHIVE_COVER_IMAGE
except AttributeError:
    COVER_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cover.png')

