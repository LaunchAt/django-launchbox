from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from launchbox.core.jsonwebtoken.models import JsonWebToken
from launchbox.core.models import TimeStampedMixin, UUIDPrimaryKeyMixin

from .service import Service


class Application(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    name = models.CharField(_('application name'), max_length=32)
    url = models.URLField(_('application url'), null=True, blank=True, default=None)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('service'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('owner'),
    )

    class Meta:
        db_table = 'launchbox_application'
        verbose_name = _('application')
        verbose_name_plural = _('applications')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name


class ApplicationToken(JsonWebToken):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('application'),
    )

    class Meta:
        db_table = 'launchbox_application_token'
        verbose_name = _('application token')
        verbose_name_plural = _('application tokens')
        ordering = ('-issued_at',)

    def __str__(self) -> str:
        jws = self.jws
        return jws[0:8] + '*' * (len(jws) - 8)


class ApplicationAdminUser(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='admin_users',
        verbose_name=_('application'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_applications',
        verbose_name=_('user'),
    )

    class Meta:
        db_table = 'launchbox_application_admin_user'
        verbose_name = _('application admin user')
        verbose_name_plural = _('application admin users')
        ordering = ('application', 'user')
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'user'],
                name='unique_user_per_application',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.application} / {self.user}'
