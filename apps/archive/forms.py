from datetime import datetime
import os
import os.path

from django import forms
from django.utils.translation import ugettext_lazy as _
import mutagen

from archive.models import Audiobook
from archive.settings import FILES_PATH
from archive.utils import ExistingFile, sha1_file

class AudiobookForm(forms.ModelForm):
    class Meta:
        model = Audiobook

    def save(self, commit=True, path=None):
        m = super(AudiobookForm, self).save(commit=False)
        m.modified = datetime.now()

        if path:
            # adding a new audiobook
            if not os.path.isdir(FILES_PATH):
                os.makedirs(FILES_PATH)
            # save the file in model

            m.source_file.save(
                os.path.basename(path),
                ExistingFile(path))

            f = open(m.source_file.path)
            m.source_sha1 = sha1_file(f)
            f.close()

        if commit:
            m.save()
