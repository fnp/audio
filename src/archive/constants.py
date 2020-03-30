from django.utils.translation import gettext_lazy as _

class status:
    WAITING = 1
    ENCODING = 2
    TAGGING = 3
    SENDING = 4

    choices = [
        (WAITING, _('Waiting')),
        (ENCODING, _('Encoding')),
        (TAGGING, _('Tagging')),
        (SENDING, _('Sending')),
    ]
