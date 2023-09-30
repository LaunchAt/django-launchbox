import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(_('uuid primary key'), primary_key=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(
        _('creation date and time'),
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        _('update date and time'),
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True
