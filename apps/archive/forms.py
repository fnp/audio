import os
import os.path
from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
import mutagen

from archive.models import Audiobook
from archive.settings import FILES_PATH
from archive.utils import ExistingFile

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
            bn = os.path.basename(path)
            ef = ExistingFile(path)
            
            m.source_file.save(bn, ef)

        if commit:
            m.save()

