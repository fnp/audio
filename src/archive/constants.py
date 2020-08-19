from django.utils.translation import gettext_lazy as _


class status:
    QUEUED = 5
    WAITING = 10
    ENCODING = 20
    TAGGING = 30
    CONVERTING_AUDIO = 40
    CONVERTING_VIDEO = 50
    ASSEMBLING_AUDIO = 60
    ASSEMBLING_VIDEO = 70
    JOINING_AUDIO_VIDEO = 80
    SENDING = 100
    SETTING_THUMBNAIL = 110

    choices = [
        (QUEUED, _("Queued")),
        (WAITING, _('Waiting')),
        (ENCODING, _('Encoding')),
        (TAGGING, _('Tagging')),
        (CONVERTING_AUDIO, _('Converting audio')),
        (CONVERTING_VIDEO, _('Converting video')),
        (ASSEMBLING_AUDIO, _('Assembling audio')),
        (ASSEMBLING_VIDEO, _('Assembling video')),
        (JOINING_AUDIO_VIDEO, _('Joining audio and video')),
        (SENDING, _('Sending')),
        (SETTING_THUMBNAIL, _('Setting thumbnail')),
    ]
