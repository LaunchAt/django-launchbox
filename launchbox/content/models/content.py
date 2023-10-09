from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from launchbox.core.models import TimeStampedMixin, UUIDPrimaryKeyMixin

from .service import Service


class Content(TimeStampedMixin, UUIDPrimaryKeyMixin, models.Model):
    body_html = models.TextField(
        _('content body html'),
        blank=True,
        null=True,
        default=None,
    )
    is_draft = models.BooleanField(_('draft'), default=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name=_('service'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('owner'),
    )

    class Meta:
        db_table = 'launchbox_content'
        verbose_name = _('content')
        verbose_name_plural = _('contents')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.body_html[0:30]}' or _('empty page')


# class ContentEdit(TimeStampedMixin, UUIDPrimaryKeyMixin, models.Model):
#     body_html = models.TextField(
#         _('content body html'),
#         blank=True,
#         null=True,
#         default=None,
#     )
#     value_json = models.JSONField(
#         _('content value json'),
#         blank=True,
#         null=True,
#         default=None,
#     )
#     content = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         related_name='+',
#         verbose_name=_('user who edit'),
#         blank=True,
#         null=True,
#         default=None,
#         editable=False,
#     )
#     edited_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         related_name='+',
#         verbose_name=_('user who edit'),
#         blank=True,
#         null=True,
#         default=None,
#         editable=False,
#     )
