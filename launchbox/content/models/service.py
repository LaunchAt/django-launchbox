from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from launchbox.core.jsonwebtoken.models import JsonWebToken
from launchbox.core.models import TimeStampedMixin, UUIDPrimaryKeyMixin


class Service(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    name = models.CharField(_('service name'), max_length=32)
    slug = models.SlugField(
        _('service slug'),
        max_length=32,
        unique=True,
        db_index=True,
    )
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name='service',
        verbose_name=_('service site'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('service owner'),
    )

    class Meta:
        db_table = 'launchbox_service'
        verbose_name = _('service')
        verbose_name_plural = _('services')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name


class ServiceToken(JsonWebToken):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('service'),
    )

    class Meta:
        db_table = 'launchbox_service_token'
        verbose_name = _('service token')
        verbose_name_plural = _('service tokens')
        ordering = ('-issued_at',)

    def __str__(self) -> str:
        jws = self.jws
        return jws[0:8] + '*' * (len(jws) - 8)
