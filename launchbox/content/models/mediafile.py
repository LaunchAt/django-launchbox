import os

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from launchbox.core.models import TimeStampedMixin, UUIDPrimaryKeyMixin

from .service import Service


class MediaFile(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    def get_upload_to(self, filename: str):
        timestamp = int(now().timestamp())
        extension = os.path.splitext(filename.lower())[-1]
        return f'{self.service.short_id}/{self.short_id}/{timestamp}{extension}'

    name = models.CharField(_('file name'), max_length=64)
    file = models.FileField(_('file'), upload_to=get_upload_to)
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name=_('service'),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('user who uploaded'),
    )

    class Meta:
        db_table = 'launchbox_media_file'
        verbose_name = _('media file')
        verbose_name_plural = _('media files')
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    @property
    def file_url(self):
        return self.file.url

    @property
    def file_size(self):
        return self.file.size
