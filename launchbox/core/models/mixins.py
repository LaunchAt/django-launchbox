import base64
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


def convert_uuid_to_short_id(uuid: uuid.UUID) -> str:
    """Get the Base32 encoded short id of the UUID.

    Args:
        uuid (UUID): The UUID to be converted.

    Returns:
        str: The Base32 encoded string of the UUID.
    """
    return base64.b32encode(uuid.bytes).decode('utf-8').rstrip('=')


def convert_short_id_to_uuid(short_id: str) -> uuid.UUID:
    """Get the UUID from Base32 encoded short id.

    Args:
        short_id (str): The short_id to be converted.

    Returns:
        uuid: The UUID from the Base32 encoded short id.
    """
    # Add padding for Base32 decoding
    padded_short_id = f'{short_id}======'
    return uuid.UUID(bytes=base64.b32decode(padded_short_id))


class UUIDPrimaryKeyModelQuerySet(models.QuerySet):
    def get_by_short_id(self, *, short_id: str) -> 'UUIDPrimaryKeyModelQuerySet':
        return self.get(id=convert_short_id_to_uuid(short_id))


# Using type: ignore to bypass mypy's type checking for this dynamic base class
class UUIDPrimaryKeyModelManager(
    models.Manager.from_queryset(UUIDPrimaryKeyModelQuerySet),  # type: ignore
):
    pass


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(
        _('uuid primary key'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    objects = UUIDPrimaryKeyModelManager()

    class Meta:
        abstract = True

    @property
    def short_id(self):
        return convert_uuid_to_short_id(self.id)


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(
        _('creation date and time'),
        auto_now_add=True,
        db_index=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        _('update date and time'),
        auto_now=True,
        db_index=True,
        editable=False,
    )

    class Meta:
        abstract = True
