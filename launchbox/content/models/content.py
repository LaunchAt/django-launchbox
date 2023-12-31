from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from launchbox.core.models import TimeStampedMixin, UUIDPrimaryKeyMixin

from .service import Service


class ContentTheme(TimeStampedMixin, UUIDPrimaryKeyMixin, models.Model):
    name = models.CharField(_('theme name'), max_length=32)
    css = models.TextField(_('theme css'), blank=True, null=True, default=None)
    url = models.URLField(_('theme style sheet url'), null=True, blank=True, default=None)
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
        db_table = 'launchbox_content_theme'
        verbose_name = _('content theme')
        verbose_name_plural = _('content themes')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name


class Content(TimeStampedMixin, UUIDPrimaryKeyMixin, models.Model):
    title = models.CharField(
        _('content title'),
        max_length=32,
        blank=True,
        null=True,
        default=None,
    )
    body_html = models.TextField(
        _('content body html'),
        blank=True,
        null=True,
        default=None,
    )
    is_draft = models.BooleanField(_('draft'), default=True)
    theme = models.ForeignKey(
        ContentTheme,
        on_delete=models.SET_NULL,
        verbose_name=_('theme'),
        blank=True,
        null=True,
        default=None,
    )
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
        return self.title or '{}'.format((self.body_html or '')[0:30]) or '{}'.format(_('empty page'))


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
