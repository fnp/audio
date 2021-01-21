from datetime import datetime
import os
import os.path

from django import forms
from django.utils.translation import gettext_lazy as _
import mutagen
from django.utils.encoding import force_bytes

from youtube.utils import get_duration
from archive.models import Audiobook
from archive.settings import FILES_PATH, NEW_PATH
from archive.utils import ExistingFile, sha1_file

class AudiobookForm(forms.ModelForm):
    class Meta:
        model = Audiobook
        exclude = []

    def save(self, commit=True, path=None):
        """ Performs normal save, with given file as an source audiobook.

            `path' is relative to NEW_PATH.
        """
        m = super(AudiobookForm, self).save(commit=False)
        m.modified = datetime.now()

        if path:
            # adding a new audiobook
            if not os.path.isdir(FILES_PATH):
                os.makedirs(FILES_PATH)
            # save the file in model

            abs_path = os.path.join(NEW_PATH, path)
            m.duration = get_duration(abs_path)
            m.source_file.save(
                path,
                ExistingFile(abs_path))

#            f = open(force_bytes(m.source_file.path))
#            m.source_sha1 = sha1_file(f)
#            f.close()

        if commit:
            m.save()
